# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2018-11-23
copyright            : (C) 2009 by Minpa Lee, MangoSystem
email                : mapplus at gmail.com
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

from qgis.core import (Qgis, QgsCoordinateReferenceSystem)
from .weblayer import WebLayer3857


class OlNaverMapsLayer(WebLayer3857):

    # Group in menu
    groupName = 'Naver Maps v5'

    # Group icon in menu
    groupIcon = 'naver_icon.png'

    # Supported EPSG projections, ordered by preference
    epsgList = [3857]

    # WGS84 bounds
    fullExtent = [124.41714675, 33.0022776231, 131.971482078, 38.6568782776]

    MIN_ZOOM_LEVEL = 6

    MAX_ZOOM_LEVEL = 17

    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540

    emitsLoadEnd = False

    def __init__(self, name, html, xyzUrl, tilePixelRatio=2):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl, tilePixelRatio=tilePixelRatio)


class OlNaverStreetLayer(OlNaverMapsLayer):

    def __init__(self):
        tmsUrl = "https://map.pstatic.net/nrb/styles/basic/1717723233/{z}/{x}/{y}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Street", html="naver_street.html", xyzUrl=None)


class OlNaverHybridLayer(OlNaverMapsLayer):

    def __init__(self):
        tmsUrl = "https://map.pstatic.net/nrb/styles/satellite/1717723233/{z}/{x}/{y}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Hybrid", html="naver_hybrid.html", xyzUrl=None)


class OlNaverSatelliteLayer(OlNaverMapsLayer):

    def __init__(self):
        tmsUrl = "https://map.pstatic.net/nrb/styles/satellite/1717723233/{z}/{x}/{y}@2x.png?mt=bg.ol.ts"
        OlNaverMapsLayer.__init__(self, name="Naver Satellite", html="naver_satellite.html", xyzUrl=None)


class OlNaverPhysicalLayer(OlNaverMapsLayer):

    def __init__(self):
        tmsUrl = "https://map.pstatic.net/nrb/styles/terrain/1717723233/{z}/{x}/{y}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Physical", html="naver_physical.html", xyzUrl=None)


class OlNaverCadastralLayer(OlNaverMapsLayer):

    def __init__(self):
        tmsUrl = "https://map.pstatic.net/nrb/styles/basic/1717723233/{z}/{x}/{y}@2x.png?mt=bg.ol.ts.lp"
        OlNaverMapsLayer.__init__(self, name="Naver Cadastral", html="naver_cadastral.html", xyzUrl=None)
