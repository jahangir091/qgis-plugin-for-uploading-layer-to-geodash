# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveLayerInGeoDASH
                                 A QGIS plugin
 This plugin saves layer in GeoDASH from qgis
                             -------------------
        begin                : 2018-04-16
        copyright            : (C) 2018 by Jahangir Alam
        email                : jahangir.cse09@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SaveLayerInGeoDASH class from file SaveLayerInGeoDASH.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .save_layer_geodash_plugin import SaveLayerInGeoDASH
    return SaveLayerInGeoDASH(iface)
