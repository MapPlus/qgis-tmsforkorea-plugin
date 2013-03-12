# -*- coding: utf-8 -*-
"""
/***************************************************************************
TMS for Korea
A QGIS plugin

                             -------------------
begin                : 2009-11-30
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
modified             : (C) 2013 by Minpa Lee, mapplus@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *

import resources_rc
import math

from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType
from openlayers_ovwidget import OpenLayersOverviewWidget

class OlLayerType:

  def __init__(self, plugin, name, icon, html, emitsLoadEnd = False):
    self.__plugin = plugin
    self.name = name
    self.icon = icon
    self.html = html
    self.emitsLoadEnd = emitsLoadEnd
    self.id = None

  def addLayer(self):
    self.__plugin.addLayer(self)


class OlLayerTypeRegistry:

  def __init__(self):
    self.__olLayerTypes = {}
    self.__layerTypeId = 0

  def add(self, layerType):
    layerType.id = self.__layerTypeId
    self.__olLayerTypes[self.__layerTypeId] = layerType
    self.__layerTypeId += 1

  def types(self):
    return self.__olLayerTypes.values()

  def getById(self, id):
    return self.__olLayerTypes[id]


class OLOverview(object):

  def __init__(self, iface, olLayerTypeRegistry):
    self.__iface = iface
    self.__olLayerTypeRegistry = olLayerTypeRegistry
    self.__dockwidget = None
    self.__oloWidget = None

  # Private
  def __setDocWidget(self):
    self.__dockwidget = QDockWidget(QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), self.__iface.mainWindow() )
    self.__dockwidget.setObjectName("dwOpenlayersOverview")
    self.__oloWidget = OpenLayersOverviewWidget(self.__iface, self.__dockwidget, self.__olLayerTypeRegistry)
    self.__dockwidget.setWidget(self.__oloWidget)

  def __initGui(self):
    self.__setDocWidget()
    self.__iface.addDockWidget( Qt.LeftDockWidgetArea, self.__dockwidget)

  def __unload(self):
    self.__dockwidget.close()
    self.__iface.removeDockWidget( self.__dockwidget )
    del self.__oloWidget
    self.__dockwidget = None

  # Public
  def setVisible(self, visible):
    if visible:
      if self.__dockwidget is None:
        self.__initGui()
    else:
      if not self.__dockwidget is None:
        self.__unload()
 

class OpenlayersPlugin:
  name = "TMS for Korea"
  targetSRS = QgsCoordinateReferenceSystem()

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

    # setup locale
    pluginDir = os.path.dirname( __file__ )
    localePath = ""
    locale = QSettings().value("locale/userLocale").toString()[0:2]
    if QFileInfo(pluginDir).exists():
      localePath = pluginDir + "/i18n/openlayers_" + locale + ".qm"
    if QFileInfo(localePath).exists():
      self.translator = QTranslator()
      self.translator.load(localePath)
      if qVersion() > '4.3.3':
        QCoreApplication.installTranslator(self.translator)

    # Layers
    self.olLayerTypeRegistry = OlLayerTypeRegistry()
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Daum Street', 'daum_icon.png', 'daum_street.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Daum Satellite', 'daum_icon.png', 'daum_satellite.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Daum Hybrid', 'daum_icon.png', 'daum_hybrid.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Daum Physical', 'daum_icon.png', 'daum_physical.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Naver Street', 'naver_icon.png', 'naver_street.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Naver Satellite', 'naver_icon.png', 'naver_satellite.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Naver Hybrid', 'naver_icon.png', 'naver_hybrid.html', False) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Naver Cadstral', 'naver_icon.png', 'naver_cadastral.html', False) )
    
    # Overview
    self.olOverview = OLOverview( iface, self.olLayerTypeRegistry )

  def initGui(self):
    # Overview
    self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
    self.overviewAddAction.setCheckable(True)
    self.overviewAddAction.setChecked(False)
    QObject.connect(self.overviewAddAction, SIGNAL("toggled(bool)"), self.olOverview.setVisible )
    self.iface.addPluginToMenu(self.name, self.overviewAddAction)
    
    # Layers
    self.layerAddActions = []
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    for layerType in self.olLayerTypeRegistry.types():
      # Create actions for adding layers
      action = QAction(QIcon(pathPlugin % layerType.icon), QApplication.translate("OpenlayersPlugin", "Add %1").arg(layerType.name), self.iface.mainWindow())
      self.layerAddActions.append(action)
      QObject.connect(action, SIGNAL("triggered()"), layerType.addLayer)
      # Add toolbar button and menu item
      self.iface.addPluginToMenu(self.name, action)

    if not self.setDefaultSRS():
      QMessageBox.critical(self.iface.mainWindow(), self.name, QApplication.translate(self.name, "Could not set Korean projection!"))
      return

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface, self.setReferenceLayer, self.targetSRS, self.olLayerTypeRegistry))

    self.layer = None
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
  def unload(self):
    # Remove the plugin menu item and icon
    for action in self.layerAddActions:
      self.iface.removePluginMenu(self.name, action)

    self.iface.removePluginMenu(self.name, self.overviewAddAction)  

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
    self.olOverview.setVisible( False )
    del self.olOverview

  def addLayer(self, layerType):
    # check layers
    mapCanvas = self.iface.mapCanvas()
    mapCanvas.mapRenderer().setProjectionsEnabled(True) 
    
    self.targetSRS = QgsCoordinateReferenceSystem(5181)   # Daum 5181
    if layerType.name.startswith('Naver'):
        self.targetSRS = QgsCoordinateReferenceSystem(5179)   # Naver 5179
        if mapCanvas.layerCount() == 0:
            mapCanvas.setExtent(QgsRectangle(90112, 1192896, 1990673, 2761664))
    else:
        if mapCanvas.layerCount() == 0:
            mapCanvas.setExtent(QgsRectangle(-30000, -60000, 494288, 988576))
        
    if QGis.QGIS_VERSION_INT >= 10900:
      mapCanvas.mapRenderer().setDestinationCrs(self.targetSRS)
    else:
      mapCanvas.mapRenderer().setDestinationSrs(self.targetSRS)
    mapCanvas.setMapUnits(self.targetSRS.mapUnits())
    
    # On the fly    
    if QGis.QGIS_VERSION_INT >= 10900:
      theCoodRS = mapCanvas.mapRenderer().destinationCrs()
    else:
      theCoodRS = mapCanvas.mapRenderer().destinationSrs()
    if theCoodRS != self.targetSRS:
      coodTrans = QgsCoordinateTransform(theCoodRS, self.targetSRS)
      extMap = mapCanvas.extent()
      extMap = coodTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
      if QGis.QGIS_VERSION_INT >= 10900:
        mapCanvas.mapRenderer().setDestinationCrs(self.targetSRS)
      else:
        mapCanvas.mapRenderer().setDestinationSrs(self.targetSRS)
      mapCanvas.freeze(False)
      mapCanvas.setMapUnits(self.targetSRS.mapUnits())
      mapCanvas.setExtent(extMap)
      
    layer = OpenlayersLayer(self.iface, self.targetSRS, self.olLayerTypeRegistry)
    layer.setLayerName(layerType.name)
    layer.setLayerType(layerType)
    if layer.isValid():
      if QGis.QGIS_VERSION_INT >= 10900:
        QgsMapLayerRegistry.instance().addMapLayers([layer])
      else:
        QgsMapLayerRegistry.instance().addMapLayer(layer)

      # last added layer is new reference
      self.setReferenceLayer(layer)
    
    if QgsMapLayerRegistry.instance().count() == 1:
      mapCanvas = self.iface.mapCanvas()
      mapCanvas.setDirty(True)
      mapCanvas.refresh()

  def setReferenceLayer(self, layer):
    self.layer = layer
    # TODO: update initial scale

  def removeLayer(self, layerId):
    layerToRemove = None
    if QGis.QGIS_VERSION_INT >= 10900:
      currentLayerId = self.layer.id()
    else:
      currentLayerId = self.layer.getLayerID()
    if self.layer != None and currentLayerId == layerId:
      self.layer = None
      # TODO: switch to next available OpenLayers layer?

  def setDefaultSRS(self):
    # Daum = default srs
    if QGis.QGIS_VERSION_INT >= 10900:
      created = self.targetSRS.createFromOgcWmsCrs('EPSG:5181')
    else:
      created = self.targetSRS.createFromEpsg(5181)
    if not created:
      google_proj_def = "+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
      isOk = self.targetSRS.createFromProj4(google_proj_def)
      if isOk:
        return True
      else:
        return False
    else:
      return True
