# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
# -*- coding: utf-8 -*-
# noinspection PyPep8Naming
"""
***************************************************************************
    speclib/__init__.py

    A python module to handle and visualize SpectralLibraries in QGIS
    ---------------------
    Beginning            : 2018-12-17
    Copyright            : (C) 2020 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this software. If not, see <http://www.gnu.org/licenses/>.
***************************************************************************
"""
import pathlib

from qgis.PyQt.QtCore import NULL, QVariant
from qgis.core import QgsSettings, QgsCoordinateReferenceSystem, QgsField, QgsFields

EDITOR_WIDGET_REGISTRY_KEY = 'SpectralProfile'
EDITOR_WIDGET_REGISTRY_NAME = 'Spectral Profile'

SPECLIB_EPSG_CODE = 4326
SPECLIB_CRS = QgsCoordinateReferenceSystem('EPSG:{}'.format(SPECLIB_EPSG_CODE))

EMPTY_VALUES = [None, NULL, QVariant(), '', 'None']

FIELD_VALUES = 'profiles'
FIELD_NAME = 'name'
FIELD_FID = 'fid'


def createStandardFields() -> QgsFields:
    from .core import create_profile_field
    fields = QgsFields()
    fields.append(create_profile_field('profiles'))
    fields.append(QgsField('name', QVariant.String))
    return fields


class SpectralLibrarySettingsKey:
    BACKGROUND_COLOR = 'BACKGROUND_COLOR'
    FOREGROUND_COLOR = 'FOREGROUND_COLOR'
    INFO_COLOR = 'INFO_COLOR'
    CROSSHAIR_COLOR = 'CROSSHAIR_COLOR'
    SELECTION_COLOR = 'SELECTION_COLOR'
    TEMPORARY_COLOR = 'TEMPORARY_COLOR'


def speclibSettings() -> QgsSettings:
    """
    Returns SpectralLibrary relevant QSettings
    :return: QSettings
    """
    return QgsSettings('EnMAP', 'speclib')


def speclibUiPath(name: str) -> str:
    """
    Returns the path to a spectral library *.ui file
    :param name: name
    :type name: str
    :return: absolute path to *.ui file
    :rtype: str
    """
    path = pathlib.Path(__file__).parent / 'ui' / name
    assert path.is_file(), f'File does not exist: {path}'
    return path.as_posix()
