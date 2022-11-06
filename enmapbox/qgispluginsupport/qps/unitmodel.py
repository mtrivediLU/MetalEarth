from typing import Dict

import numpy as np

from qgis.PyQt.QtCore import Qt, NULL, QAbstractListModel, QModelIndex
from qgis.PyQt.QtGui import QIcon
from .utils import UnitLookup, METRIC_EXPONENTS, datetime64

BAND_INDEX = 'Band Index'
BAND_NUMBER = 'Band Number'


class UnitModel(QAbstractListModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.mUnits: Dict[str, tuple] = dict()

    def setAllowEmptyUnit(self,
                          allowEmpty: bool,
                          text: str = '',
                          tooltip: str = 'None',
                          icon: QIcon = QIcon()):

        self.beginResetModel()
        if allowEmpty:
            self.mUnits[None] = (None, text, tooltip, icon)
        else:
            if None in self.mUnits.keys():
                self.mUnits.pop(None)

        items = sorted(self.mUnits.values(), key=lambda v: v[0] is not None)
        self.mUnits.clear()
        for item in items:
            self.mUnits[item[0]] = item

        self.endResetModel()

    def __contains__(self, item):
        return item in self.mUnits

    def __iter__(self):
        return iter(self.mUnits.keys())

    def __getitem__(self, slice):
        return list(self.mUnits.keys())[slice]

    def rowCount(self, parent=None, *args, **kwargs) -> int:
        return len(self.mUnits)

    def findUnit(self, value: str) -> str:
        """
        Returns a matching unit string, e.g. nm for Nanometers
        :param value:
        :return:
        """

        if value in self.mUnits.keys():
            return value

        baseUnit = UnitLookup.baseUnit(value)
        if baseUnit in self.mUnits.keys():
            return baseUnit

        for unit, description in self.mUnits.items():
            if self.unitMatch(value, description):
                return unit
        return None

    def unitMatch(self, unit: str, description: tuple) -> bool:
        for p in description:
            if p == unit or str(p).lower() == str(unit).lower():
                return True
        return False

    def removeUnit(self, unit: str):
        """
        Removes a unit from this model
        :param unit: str
        """
        unit = self.findUnit(unit)
        units = list(self.mUnits.keys())
        if unit in units:
            row = units.index(unit)
            self.beginRemoveRows(QModelIndex(), row, row)
            self.mUnits.pop(unit)
            self.endRemoveRows()

    def addUnit(self,
                unit: str,
                description: str = None,
                tooltip: str = None,
                icon: str = None):
        """
        Adds a unit to the unit model
        :param unit:
        :type unit:
        :param description:
        :type description:
        :param tooltip:
        :type tooltip:
        :return:
        :rtype:
        """
        if description is None:
            description = unit

        if unit not in self.mUnits.keys():
            t = (unit, description, tooltip, icon)
            r = len(self.mUnits)
            self.beginInsertRows(QModelIndex(), r, r)
            self.mUnits[unit] = t
            self.endInsertRows()

    def unitIndex(self, unit: str) -> QModelIndex:
        """
        Returns the QModelIndex of a unit.
        :param unit:
        :type unit:
        :return:
        :rtype:
        """
        for i, description in enumerate(self.mUnits.values()):
            if self.unitMatch(unit, description):
                return self.index(i, 0)
        return QModelIndex()

    def unitData(self, unit: str, role=Qt.DisplayRole):
        """
        Convenience function to access unit metadata
        :param unit:
        :type unit:
        :param role:
        :type role:
        :return:
        :rtype:
        """
        return self.data(self.unitIndex(unit), role=role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        unit, description, tooltip, icon = list(self.mUnits.values())[index.row()]

        if role == Qt.DisplayRole:
            return description
        if role == Qt.ToolTipRole:
            return tooltip
        if role == Qt.DecorationRole:
            return icon
        if role == Qt.UserRole:
            return unit


class UnitConverterFunctionModel(object):

    def __init__(self):

        # look-up table with functions to convert from unit1 to unit2, with unit1 != unit2 and
        # unit1 != None and unit2 != None
        self.mLUT = dict()

        self.func_return_band_index = lambda v, *args: np.arange(len(v))
        self.func_return_band_number = lambda v, *args: np.arange(len(v)) + 1
        self.func_return_none = lambda v, *args: None
        self.func_return_same = lambda v, *args: v
        self.func_return_decimalyear = lambda v, *args: UnitLookup.convertDateUnit(v, 'DecimalYear')

        # metric units
        for u1, e1 in METRIC_EXPONENTS.items():
            for u2, e2 in METRIC_EXPONENTS.items():
                key = (u1, u2)
                if key not in self.mLUT.keys():
                    if u1 != u2:
                        self.mLUT[key] = lambda v, *args, k1=u1, k2=u2: UnitLookup.convertMetricUnit(v, k1, k2)

        # time units
        # convert between DecimalYear and DateTime stamp
        self.mLUT[('DecimalYear', 'DateTime')] = lambda v, *args: datetime64(v)
        self.mLUT[('DateTime', 'DecimalYear')] = lambda v, *args: UnitLookup.convertDateUnit(v, 'DecimalYear')

        # convert to DOY (reversed operation is not possible)
        self.mLUT[('DecimalYear', 'DOY')] = lambda v, *args: UnitLookup.convertDateUnit(v, 'DOY')
        self.mLUT[('DateTime', 'DOY')] = lambda v, *args: UnitLookup.convertDateUnit(v, 'DOY')

    def convertFunction(self, unitSrc: str, unitDst: str):
        if unitDst == BAND_INDEX:
            return self.func_return_band_index
        elif unitDst == BAND_NUMBER:
            return self.func_return_band_number

        unitSrc = UnitLookup.baseUnit(unitSrc)
        unitDst = UnitLookup.baseUnit(unitDst)
        if unitSrc is None or unitDst is None:
            return self.func_return_none
        if unitSrc == unitDst:
            return self.func_return_same
        key = (unitSrc, unitDst)
        if key not in self.mLUT.keys():
            s = ""
        return self.mLUT.get((unitSrc, unitDst), self.func_return_none)


class XUnitModel(UnitModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.addUnit(BAND_NUMBER, description=BAND_NUMBER)
        self.addUnit(BAND_INDEX, description=BAND_INDEX)
        for u in ['Nanometers',
                  'Micrometers',
                  'Millimeters',
                  'Meters',
                  'Kilometers']:
            baseUnit = UnitLookup.baseUnit(u)
            assert isinstance(baseUnit, str), u
            self.addUnit(baseUnit, description='{} [{}]'.format(u, baseUnit))

        self.addUnit('DateTime', description='Date Time')
        self.addUnit('DecimalYear', description='Decimal Year')
        self.addUnit('DOY', description='Day of Year')

    def findUnit(self, unit):
        if unit in [None, NULL]:
            unit = BAND_NUMBER
        return super(XUnitModel, self).findUnit(unit)
