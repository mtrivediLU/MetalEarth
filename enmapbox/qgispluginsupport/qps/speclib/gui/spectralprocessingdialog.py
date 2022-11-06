import datetime
import json
import os
import pathlib
import typing
from json import JSONDecodeError
from typing import Dict

from processing import createContext
from processing.gui.AlgorithmDialogBase import AlgorithmDialogBase
from qgis.PyQt.QtCore import pyqtSignal, QObject, QModelIndex, Qt, QTimer, \
    QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QDialog, \
    QPushButton, QSizePolicy
from qgis.core import QgsEditorWidgetSetup, QgsProcessing, QgsProcessingFeedback, QgsProcessingContext, QgsVectorLayer, \
    QgsProcessingRegistry, QgsMapLayer, QgsPalettedRasterRenderer, \
    QgsApplication, Qgis, QgsProcessingModelAlgorithm, QgsProcessingAlgorithm, QgsFeature, \
    QgsProcessingParameterRasterLayer, QgsProcessingOutputRasterLayer, QgsProject, QgsProcessingParameterDefinition, \
    QgsRasterLayer, \
    QgsMapLayerModel, QgsProcessingParameterRasterDestination, QgsFields, QgsProcessingOutputLayerDefinition, \
    QgsRasterFileWriter, QgsRasterBlockFeedback, QgsRasterPipe, QgsProcessingUtils, QgsField, \
    QgsProcessingParameterMultipleLayers
from qgis.core import QgsRasterDataProvider
from qgis.gui import QgsMessageBar, QgsProcessingAlgorithmDialogBase, QgsPanelWidget, QgsProcessingParametersGenerator
from qgis.gui import QgsProcessingContextGenerator, QgsProcessingParameterWidgetContext, \
    QgsProcessingToolboxProxyModel, QgsProcessingRecentAlgorithmLog, QgsProcessingParametersWidget, \
    QgsAbstractProcessingParameterWidgetWrapper, QgsGui, QgsProcessingGui, \
    QgsProcessingHiddenWidgetWrapper
from .. import speclibSettings, EDITOR_WIDGET_REGISTRY_KEY
from ..core import is_profile_field, supports_field
from ..core.spectrallibrary import SpectralLibraryUtils
from ..core.spectrallibraryrasterdataprovider import VectorLayerFieldRasterDataProvider, createRasterLayers, \
    SpectralProfileValueConverter, FieldToRasterValueConverter
from ..core.spectralprofile import prepareProfileValueDict, \
    encodeProfileValueDict, ProfileEncoding
from ..gui.spectralprofilefieldcombobox import SpectralProfileFieldComboBox
from ...processing.processingalgorithmdialog import ProcessingAlgorithmDialog
from ...qgsrasterlayerproperties import QgsRasterLayerSpectralProperties
from ...utils import rasterArray, iconForFieldType, numpyToQgisDataType, qgsRasterLayer

LUT_RASTERFILEWRITER_ERRORS: Dict[int, str] = {
    QgsRasterFileWriter.WriterError.SourceProviderError: 'SourceProviderError',
    QgsRasterFileWriter.WriterError.DestProviderError: 'DestProviderError',
    QgsRasterFileWriter.WriterError.CreateDatasourceError: 'CreateDatasourceError',
    QgsRasterFileWriter.WriterError.WriteError: 'WriteError',
    QgsRasterFileWriter.WriterError.NoDataConflict: 'Internal error if a value used '
                                                    'for "no data" was found in input',
    QgsRasterFileWriter.WriterError.WriteCanceled: 'Writing was manually canceled.',

}


def has_raster_input(alg: QgsProcessingAlgorithm) -> bool:
    if not isinstance(alg, QgsProcessingAlgorithm):
        return False
    for input in alg.parameterDefinitions():
        if isinstance(input, QgsProcessingParameterRasterLayer):
            return True
    return False


def has_raster_output(alg: QgsProcessingAlgorithm) -> bool:
    if not isinstance(alg, QgsProcessingAlgorithm):
        return False

    for output in alg.outputDefinitions():
        if isinstance(output, QgsProcessingOutputRasterLayer):
            return True
    return False


def has_raster_io(alg: QgsProcessingAlgorithm) -> bool:
    return has_raster_input(alg) and has_raster_output(alg)


class SpectralProcessingAppliers(QObject):

    def __init__(self):
        super().__init__()


class SpectralProcessingAlgorithmModel(QgsProcessingToolboxProxyModel):
    """
    This proxy model filters out all QgsProcessingAlgorithms that do not use
    SpectralProcessingProfiles
    """

    def __init__(self,
                 parent: QObject,
                 registry: QgsProcessingRegistry = None,
                 recentLog: QgsProcessingRecentAlgorithmLog = None):
        super().__init__(parent, registry, recentLog)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):

        sourceIdx = self.toolboxModel().index(sourceRow, 0, sourceParent)
        if self.toolboxModel().isAlgorithm(sourceIdx):
            alg = self.toolboxModel().algorithmForIndex(sourceIdx)
            return super().filterAcceptsRow(sourceRow, sourceParent) and has_raster_input(alg)
        else:
            return super().filterAcceptsRow(sourceRow, sourceParent)


class SpectralProcessingRasterDestination(QgsAbstractProcessingParameterWidgetWrapper):

    def __init__(self,
                 parameter,
                 dialogType: QgsProcessingGui.WidgetType = QgsProcessingGui.Standard,
                 parent: QObject = None):
        self.mLabel: QLabel = None
        self.mFieldComboBox: SpectralProfileFieldComboBox = None
        self.mFieldName: str = None
        self.mFields: QgsFields = QgsFields()
        super(SpectralProcessingRasterDestination, self).__init__(parameter, dialogType, parent)

    def setFields(self, fields: QgsFields):
        self.mFields = fields
        # self.mFieldComboBox.setFields(fields)

    def createLabel(self) -> QLabel:
        # l = QLabel(f'<html><img width="20"px" height="20"
        # src=":/qps/ui/icons/profile.svg">{self.parameterDefinition().description()}</html>')
        # label = QLabel(f'{self.parameterDefinition().description()} (to field)')
        label = QLabel(f'<html> <img src=":/qps/ui/icons/raster_to_field.svg"/>   '
                       f'{self.parameterDefinition().description()}</html>')
        label.setToolTip('An existing or new field to write raster values to')
        self.mLabel = label
        return label

    def wrappedLabel(self) -> QLabel:
        if not isinstance(self.mLabel, QLabel):
            self.mLabel = self.createLabel()
        return self.mLabel

    def createWrappedWidget(self, context: QgsProcessingContext) -> QWidget:

        if not isinstance(self.mFieldComboBox, SpectralProfileFieldComboBox):
            self.mFieldComboBox = self.createWidget()
            self.mFieldComboBox.setObjectName(self.parameterDefinition().name())
        return self.mFieldComboBox

    def createWidget(self):
        cb = QComboBox()
        cb.setEditable(True)
        for f in self.mFields:
            cb.addItem(iconForFieldType(f), f.name(), f)
        is_optional = self.parameterDefinition().flags() & QgsProcessingParameterDefinition.FlagOptional
        if is_optional:
            pass
        cb.currentTextChanged.connect(self.setValue)
        self.mFieldComboBox = cb
        return cb

    def setValue(self, value):

        old = self.mFieldName
        if isinstance(value, str):
            self.mFieldName = value

        if old != self.mFieldName:
            self.widgetValueHasChanged.emit(self)

    def setWidgetValue(self, value, context: QgsProcessingContext):
        if isinstance(self.mFieldComboBox, QComboBox) and isinstance(self.mFields, QgsFields):
            if isinstance(value, str):
                value2 = self.pathToFieldName(value)
                for i in range(self.mFieldComboBox.count()):
                    field: QgsField = self.mFieldComboBox.itemData(i, Qt.UserRole)
                    if field.name() == value or field.name() == value2:
                        self.mFieldComboBox.setCurrentIndex(i)
                        return
                # not found. set text for new field
                self.mFieldComboBox.setCurrentText(value2)

    @classmethod
    def pathToFieldName(cls, path: str) -> str:
        name, ext = os.path.splitext(pathlib.Path(path).name)
        suffix = f'{QgsProcessing.TEMPORARY_OUTPUT}_'
        name = name.replace(suffix, '')
        return name

    def widgetValue(self):
        if isinstance(self.mFieldComboBox, QComboBox):
            path = self.mFieldComboBox.currentText()
            bn, ext = os.path.splitext(path)
            if ext == '':
                ext = self.parameterDefinition().defaultFileExtension()
                path = f'{bn}.{ext}'
            return f'{QgsProcessing.TEMPORARY_OUTPUT}_{path}'
        return None


class SpectralProcessingRasterLayerWidgetWrapper(QgsAbstractProcessingParameterWidgetWrapper):

    def __init__(self,
                 parameter: QgsProcessingParameterDefinition = None,
                 dialogType: QgsProcessingGui.WidgetType = QgsProcessingGui.Standard,
                 parent: QObject = None
                 ):

        assert isinstance(parameter, QgsProcessingParameterRasterLayer)
        self.mMapLayerWidget: QWidget = None
        self.mMapLayerModel: QgsMapLayerModel = None

        self.mLabel: QLabel = None

        super(SpectralProcessingRasterLayerWidgetWrapper, self).__init__(parameter, dialogType, parent)
        self.mProfileField: str = None

    def createWidget(self):

        model = QgsMapLayerModel(self, self.widgetContext().project())
        self.mMapLayerModel = model

        param = self.parameterDefinition()
        is_optional = param.flags() & QgsProcessingParameterDefinition.FlagOptional
        if is_optional:
            model.setAllowEmptyLayer(True)

        mapLayerWidget = None
        if isinstance(param, QgsProcessingParameterRasterLayer):
            cb = QComboBox()
            cb.setModel(model)
            cb.currentIndexChanged.connect(lambda idx, m=model: self.onIndexChanged(idx, m))
            mapLayerWidget = cb
        else:
            raise NotImplementedError()

        self.mMapLayerWidget = mapLayerWidget
        return mapLayerWidget

    def onIndexChanged(self, idx, model):
        layer = model.data(model.index(idx, 0), QgsMapLayerModel.LayerRole)
        self.setValue(layer)

    def createWrappedWidget(self, context: QgsProcessingContext) -> QWidget:

        if not isinstance(self.mMapLayerWidget, QWidget):
            self.mMapLayerWidget = self.createWidget()
        return self.mMapLayerWidget

    def setWidgetValue(self, value, context: QgsProcessingContext):
        if isinstance(self.mMapLayerWidget, QComboBox):
            if isinstance(value, str):

                for i in range(self.mMapLayerWidget.count()):
                    role1 = self.mMapLayerWidget.itemData(i, Qt.DisplayRole)
                    role2 = self.mMapLayerWidget.itemData(i, Qt.UserRole)
                    if value == role1 or value == role2:
                        self.mMapLayerWidget.setCurrentIndex(i)
                        return

    def widgetValue(self):
        if isinstance(self.mMapLayerWidget, QWidget):
            if isinstance(self.mMapLayerWidget, QComboBox):
                return self.mMapLayerWidget.currentData(QgsMapLayerModel.LayerRole)
            else:
                raise NotImplementedError()

        return None

    def createLabel(self) -> QLabel:
        # l = QLabel(f'<html><img width="20"px" height="20"
        # src=":/qps/ui/icons/profile.svg">{self.parameterDefinition().description()}</html>')
        param = self.parameterDefinition()
        label = None

        if isinstance(param, QgsProcessingParameterRasterLayer):
            label = QLabel(f'<html><img src=":/qps/ui/icons/field_to_raster.svg">   '
                           f'{self.parameterDefinition().description()}</html>')
            label.setToolTip('A field whose values will be converted into a temporary raster image')
        elif isinstance(param, QgsProcessingParameterMultipleLayers):
            label = QLabel(f'<html><img src=":/qps/ui/icons/field_to_raster.svg">   '
                           f'{self.parameterDefinition().description()}')
            label.setToolTip('A set of fiels whose values will be converted into temporary raster images')
        else:
            raise NotImplementedError()
        self.mLabel = label
        return label

    def wrappedLabel(self) -> QLabel:
        if not isinstance(self.mLabel, QLabel):
            self.mLabel = self.createLabel()
        return self.mLabel

    def wrappedWidget(self) -> QWidget:
        if not isinstance(self.mMapLayerWidget, QComboBox):
            self.mMapLayerWidget = self.createWidget()
        return self.mMapLayerWidget

    def setValue(self, value):

        old = self.mProfileField
        if isinstance(value, QgsRasterLayer) and isinstance(value.dataProvider(), VectorLayerFieldRasterDataProvider):
            dp: VectorLayerFieldRasterDataProvider = value.dataProvider()
            self.mProfileField = dp.activeField()

        if old != self.mProfileField:
            self.widgetValueHasChanged.emit(self)

    def value(self):

        return self.mProfileField

        if self.mDialogType == QgsProcessingGui.Modeler:
            return self.widget.windowTitle() + '+Modeler'
        elif self.mDialogType == QgsProcessingGui.Batch:
            return self.widget.windowTitle() + '+Batch'
        else:
            return self.widget.windowTitle() + '+Std'


class SpectralProcessingModelCreatorAlgorithmWrapper(QgsProcessingParametersWidget):
    """
    A wrapper to keep a references on QgsProcessingAlgorithm
    and related parameter values and widgets
    """
    sigParameterValueChanged = pyqtSignal(str)
    sigVerificationChanged = pyqtSignal(bool)

    def __init__(self,
                 alg: QgsProcessingAlgorithm,
                 speclib: QgsVectorLayer,
                 processingContext: QgsProcessingContext,

                 parent: QWidget = None):
        assert isinstance(speclib, QgsVectorLayer)

        super().__init__(alg, parent)
        # self.alg: QgsProcessingAlgorithm = alg.create({})
        self.name: str = self.algorithm().displayName()

        # internal list of layers + internal project
        self.mExampleLayers: typing.List[QgsRasterLayer] = []
        self.mProject: QgsProject = QgsProject()
        self.mProject.setTitle('SpectralProcessing')

        self.mSpeclib: QgsVectorLayer = speclib
        self.mSpeclib.attributeAdded.connect(self.updateExampleLayers)
        self.mSpeclib.attributeDeleted.connect(self.updateExampleLayers)
        self.updateExampleLayers()

        self.mParameterWidgets: typing.Dict[str, QWidget] = dict()
        self.mOutputWidgets: typing.Dict[str, QWidget] = dict()

        # self.parameterValuesDefault: typing.Dict[str, typing.Any] = dict()
        self.mParameterValues: typing.Dict[str, typing.Any] = dict()

        self.mWrappers = {}
        self.mExtra_parameters = {}
        if processingContext is None:
            processingContext = QgsProcessingContext()

        self.mProcessing_context: QgsProcessingContext = processingContext
        self.mProcessing_context.setProject(self.mProject)

        class ContextGenerator(QgsProcessingContextGenerator):

            def __init__(self, context):
                super().__init__()
                self.mProcessingContext = context

            def processingContext(self):
                return self.mProcessingContext

        self.mContextGenerator = ContextGenerator(self.mProcessing_context)

        self.initWidgets()
        self.mTooltip: str = ''

        self.mIs_active: bool = True

    def addParameterWidget(self, parameter: QgsProcessingParameterDefinition, widget: QWidget,
                           stretch: int = ...) -> None:

        super().addParameterWidget(parameter, widget, stretch)
        self.mParameterWidgets[parameter.name()] = widget

    def parameterWidget(self, name: str) -> QWidget:
        return self.mParameterWidgets.get(name, None)

    def addOutputWidget(self, widget: QWidget, stretch: int = ...) -> None:
        super().addOutputWidget(widget, stretch)
        self.mOutputWidgets[widget.objectName()] = widget

    def outputWidget(self, name: str) -> QWidget:
        return self.mOutputWidgets.get(name, None)

    def initWidgets(self):
        super().initWidgets()
        # Create widgets and put them in layouts
        widget_context = QgsProcessingParameterWidgetContext()
        widget_context.setProject(self.mProject)

        for param in self.algorithm().parameterDefinitions():
            if param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            # if isinstance(param, (SpectralProcessingProfiles, SpectralProcessingProfilesSink)):
            #    continue
            if param.isDestination():
                continue

            if isinstance(param, QgsProcessingParameterRasterLayer):
                # workaround https://github.com/qgis/QGIS/issues/46673
                wrapper = SpectralProcessingRasterLayerWidgetWrapper(param, QgsProcessingGui.Standard)
            else:
                wrapper = QgsGui.processingGuiRegistry().createParameterWidgetWrapper(param, QgsProcessingGui.Standard)

            wrapper.setWidgetContext(widget_context)
            wrapper.registerProcessingContextGenerator(self.mContextGenerator)
            wrapper.registerProcessingParametersGenerator(self)
            wrapper.widgetValueHasChanged.connect(self.parameterWidgetValueChanged)
            # store wrapper instance
            self.mWrappers[param.name()] = wrapper

            label = wrapper.createWrappedLabel()
            self.addParameterLabel(param, label)
            processing_context = self.mProcessing_context
            widget = wrapper.createWrappedWidget(processing_context)
            stretch = wrapper.stretch()
            self.addParameterWidget(param, widget, stretch)

        for output in self.algorithm().destinationParameterDefinitions():
            if output.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue

            if isinstance(output, QgsProcessingParameterRasterDestination):
                # raster outputs will be written to new or existing spectral profile columns
                wrapper = SpectralProcessingRasterDestination(output, QgsProcessingGui.Standard)
                wrapper.setFields(self.mSpeclib.fields())

            else:
                wrapper = QgsGui.processingGuiRegistry().createParameterWidgetWrapper(output, QgsProcessingGui.Standard)

            wrapper.setWidgetContext(widget_context)
            wrapper.registerProcessingContextGenerator(self.mContextGenerator)
            wrapper.registerProcessingParametersGenerator(self)
            self.mWrappers[output.name()] = wrapper

            label = wrapper.createWrappedLabel()
            if label is not None:
                self.addOutputLabel(label)

            widget = wrapper.createWrappedWidget(self.mProcessing_context)
            self.addOutputWidget(widget, wrapper.stretch())

        for wrapper in list(self.mWrappers.values()):
            wrapper.postInitialize(list(self.mWrappers.values()))

    def parameterWidgetValueChanged(self, wrapper: QgsAbstractProcessingParameterWidgetWrapper):

        # print(f'new value: {self.name}:{wrapper}= {wrapper.parameterValue()} = {wrapper.widgetValue()}')
        # self.verify(self.mTestBlocks)
        self.mParameterValues[wrapper.parameterDefinition().name()] = wrapper.widgetValue()
        self.sigParameterValueChanged.emit(wrapper.parameterDefinition().name())

    def createProcessingParameters(self, include_default=True):
        parameters = {}
        for p, v in self.mExtra_parameters.items():
            parameters[p] = v

        for param in self.algorithm().parameterDefinitions():
            if param.flags() & QgsProcessingParameterDefinition.FlagHidden:
                continue
            if not param.isDestination():
                try:
                    wrapper = self.mWrappers[param.name()]
                except KeyError:
                    continue

                widget = wrapper.wrappedWidget()

                if not isinstance(wrapper, QgsProcessingHiddenWidgetWrapper) and widget is None:
                    continue

                value = wrapper.parameterValue()
                if param.defaultValue() != value or include_default:
                    parameters[param.name()] = value

                if not param.checkValueIsAcceptable(value):
                    raise AlgorithmDialogBase.InvalidParameterValue(param, widget)
            else:
                # if self.in_place and param.name() == 'OUTPUT':
                #    parameters[param.name()] = 'memory:'
                #    continue

                try:
                    wrapper = self.mWrappers[param.name()]
                except KeyError:
                    continue

                widget = wrapper.wrappedWidget()
                value = wrapper.parameterValue()

                dest_project = None
                if wrapper.customProperties().get('OPEN_AFTER_RUNNING'):
                    dest_project = QgsProject.instance()

                if value and isinstance(value, QgsProcessingOutputLayerDefinition):
                    value.destinationProject = dest_project
                if value and (param.defaultValue() != value or include_default):
                    parameters[param.name()] = value

                    # context = createContext()
                    context = self.mProcessing_context
                    ok, error = param.isSupportedOutputValue(value, context)
                    if not ok:
                        raise AlgorithmDialogBase.InvalidOutputExtension(widget, error)

        return self.algorithm().preprocessParameters(parameters)

    def updateExampleLayers(self):

        self.mExampleLayers.clear()
        self.mExampleLayers.extend(createRasterLayers(self.mSpeclib))

        self.mProject.removeAllMapLayers()
        self.mProject.addMapLayers(self.mExampleLayers)

    def exampleLayers(self) -> typing.List[QgsRasterLayer]:
        return self.mExampleLayers[:]

    def __hash__(self):
        return hash((self.algorithm().name(), id(self)))


class SpectralProcessingDialog(QgsProcessingAlgorithmDialogBase):
    sigSpectralProcessingModelChanged = pyqtSignal()
    sigAboutToBeClosed = pyqtSignal()

    def __init__(self, *args, speclib: QgsVectorLayer = None, parent: QWidget = None, **kwds):
        super().__init__(parent=parent)
        # QgsProcessingContextGenerator.__init__(self)
        self.mDialogName = 'Spectral Processing Dialog'
        self.setWindowIcon(QIcon(r':/qps/ui/icons/profile_processing.svg'))
        self.btnAlgorithm: QPushButton = QPushButton('Algorithm')
        self.btnAlgorithm.setIcon(QIcon(':/images/themes/default/processingAlgorithm.svg'))
        self.btnAlgorithm.clicked.connect(self.onSetAlgorithm)

        self.mTemporaryRaster: typing.List[str] = []
        self.tbAlgorithmName: QLineEdit = QLineEdit()
        self.tbAlgorithmName.setPlaceholderText('Select a raster processing algorithm / model')
        self.tbAlgorithmName.setReadOnly(True)
        self.tbAlgorithmName.setAutoFillBackground(True)
        self.tbAlgorithmName.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        self.cbSelectedFeaturesOnly = QCheckBox('Only process selected features')

        self.mTopGrid = QGridLayout()
        self.mTopGrid.addWidget(self.btnAlgorithm, 0, 0)
        self.mTopGrid.addWidget(self.tbAlgorithmName, 0, 1)
        self.mTopGrid.addWidget(self.cbSelectedFeaturesOnly, 1, 0, 1, 2)

        # self.btnAlgorithm.clicked.connect(self.actionSetAlgorithm.trigger)
        self.layout().insertLayout(0, self.mTopGrid)
        self.mProcessingAlgorithmModel: SpectralProcessingAlgorithmModel = SpectralProcessingAlgorithmModel(self)

        self.mSpeclib: QgsVectorLayer = None
        self.mAlg: QgsProcessingAlgorithm = None
        self.mPanelWidget: SpectralProcessingModelCreatorAlgorithmWrapper = None
        self.mProcessingFeedback: QgsProcessingFeedback = QgsProcessingFeedback()
        self.mProcessingContext: QgsProcessingContext = createContext(self.mProcessingFeedback)
        self.mProcessingContext.setTransformContext(QgsProject.instance().transformContext())
        self.mProcessingFeedback.progressChanged.connect(self.setPercentage)
        self.mProcessingWidgetContext: QgsProcessingParameterWidgetContext = QgsProcessingParameterWidgetContext()

        self.mProcessingAlgParametersStore: dict = dict()

        # self.mProcessingModelWrapper: SpectralProcessingModelCreatorAlgorithmWrapper = None

        self.mTestProfile = QgsFeature()
        self.mCurrentFunction: QgsProcessingAlgorithm = None

        self.updateGui()

        if isinstance(speclib, QgsVectorLayer):
            self.setSpeclib(speclib)

            # load default values from last start
            settings = speclibSettings()
            K = self.__class__.__name__
            algId = settings.value(f'{K}/algorithmId', None)
            if algId:
                s = ""
                alg: QgsProcessingAlgorithm = QgsApplication.processingRegistry().algorithmById(algId)
                if isinstance(alg, QgsProcessingAlgorithm):
                    self.setAlgorithm(alg)
                    context = self.processingContext()

                    try:
                        parJson = settings.value(f'{K}/algorithmParameters', '')
                        parameters = json.loads(parJson)
                    except (JSONDecodeError, Exception) as ex:
                        parameters = None
                    if isinstance(parameters, dict):

                        wrapper = self.processingModelWrapper()
                        for k, value in parameters.items():
                            w = wrapper.mWrappers.get(k)
                            if isinstance(w, QgsAbstractProcessingParameterWidgetWrapper):
                                w.setWidgetValue(value, context)
                    else:
                        wrapper = self.processingModelWrapper()
                        for k, w in wrapper.mWrappers.items():
                            if isinstance(w, SpectralProcessingRasterLayerWidgetWrapper):
                                s = ""
                        s = ""

    def close(self):

        # save settings

        settings = speclibSettings()
        K = self.__class__.__name__
        alg = self.algorithm()
        if isinstance(alg, QgsProcessingAlgorithm):
            settings.setValue(f'{K}/algorithmId', self.algorithm().id())
            try:
                parameters = self.processingModelWrapper().createProcessingParameters()
                parameters2 = dict()
                for k, v in parameters.items():
                    if isinstance(v, QgsMapLayer):
                        v = v.name()
                    if isinstance(v, (str, int, float, list)):
                        parameters2[k] = v
                settings.setValue(f'{K}/algorithmParameters', json.dumps(parameters2))
            except Exception as ex:
                pass

        self.sigAboutToBeClosed.emit()
        super().close()

    def setMainMessageBar(self, messageBar):
        self.mProcessingWidgetContext.setMessageBar(messageBar)

    def onSetAlgorithm(self):

        d = ProcessingAlgorithmDialog(self)
        d.setAlgorithmModel(self.mProcessingAlgorithmModel)

        if d.exec_() == QDialog.Accepted:
            alg = d.algorithm()
            if isinstance(alg, QgsProcessingAlgorithm):
                self.setAlgorithm(alg)

    def processingAlgorithm(self) -> QgsProcessingAlgorithm:
        return self.algorithm()

    def processingContext(self) -> QgsProcessingContext:
        return self.mProcessingContext

    def processingParameterWidgetContext(self) -> QgsProcessingParameterWidgetContext:
        return self.mProcessingWidgetContext

    def processingFeedback(self) -> QgsProcessingFeedback:
        return self.mProcessingFeedback

    def runAlgorithm(self, fail_fast: bool = False) -> None:
        """
        Runs the QgsProcessingAlgorithm with the specified settings
        """

        self.mTemporaryRaster.clear()

        TEMP_FOLDER = QgsProcessingUtils.generateTempFilename('')
        self.mProcessingFeedback.setProgress(int(0))
        wrapper = self.processingModelWrapper()
        if not isinstance(wrapper, SpectralProcessingModelCreatorAlgorithmWrapper):
            return None

        speclib: QgsVectorLayer = self.speclib()
        if not speclib.isEditable():
            self.log(f'Spectral Library "{speclib.name()}" is not editable', isError=True)
            self.showLog()
            return None

        alg: QgsProcessingAlgorithm = wrapper.algorithm()
        parameters = None
        try:
            rasterblockFeedback = QgsRasterBlockFeedback()

            processingContext: QgsProcessingContext = self.processingContext()
            processingFeedback = processingContext.feedback()
            # todo: set more context variables
            # processingContext.setFeedback(processingFeedback)

            parameters = wrapper.createProcessingParameters()
            # self.tabWidget.setCurrentWidget(self.tabLog)

            # save parameters
            self.log(f'Save parameters for {alg.id()}')
            self.mProcessingAlgParametersStore[alg.id()] = parameters

            transformContext = processingContext.transformContext()
            # copy and replace input raster's with temporary data sets
            # that contain spectral profiles

            self.log('Calculate feature intersection')
            affected_features = set()

            if self.selectedFeaturesOnly():
                affected_features.update(speclib.selectedFeatureIds())

            for k, v in parameters.items():
                if isinstance(v, QgsRasterLayer) and isinstance(v.dataProvider(), VectorLayerFieldRasterDataProvider):
                    dp: VectorLayerFieldRasterDataProvider = v.dataProvider()
                    fids = dp.activeFeatureIds()
                    if len(affected_features) == 0:
                        affected_features.update(fids)
                    else:
                        affected_features.intersection_update(fids)

            if len(affected_features) == 0:
                self.log('Feature ID of selected spectral profile images do not overlap', isError=True)
                return None

            activeFeatures = list(self.speclib().getFeatures(sorted(affected_features)))
            activeFeatureIDs = [f.id() for f in activeFeatures]

            if len(activeFeatureIDs) == 0:
                self.log('No active features process', isError=True)
                return None
            else:
                self.log(f'Process {len(affected_features)} features')

            parametersHard = parameters.copy()
            self.log('Make virtual raster(s) permanent')

            for k, v in parametersHard.items():
                param = alg.parameterDefinition(k)
                if isinstance(v, QgsRasterLayer) and isinstance(v.dataProvider(), VectorLayerFieldRasterDataProvider):
                    dp: VectorLayerFieldRasterDataProvider = v.dataProvider().clone()
                    dp.setActiveFeatures(activeFeatures)

                    # file_name = QgsProcessingUtils.generateTempFilename(f'{k}.tif')
                    file_name = TEMP_FOLDER + f'{k}.tif'
                    self.writeTemporaryRaster(dp, file_name, rasterblockFeedback, transformContext)
                    parametersHard[k] = file_name

                elif isinstance(param, QgsProcessingParameterRasterDestination):
                    file_name = TEMP_FOLDER + f'{v}'
                    parametersHard[k] = file_name
                    s = ""
            from processing.gui.AlgorithmExecutor import execute as executeAlg

            self.log(f'Execute algorithm: {alg.id()} ...')
            t0 = datetime.datetime.now()
            ok, results = executeAlg(alg,
                                     parametersHard,
                                     context=processingContext,
                                     feedback=processingFeedback,
                                     catch_exceptions=True)

            self.log(processingFeedback.htmlLog(), isError=not ok)
            self.log(f'Execution time: {datetime.datetime.now() - t0}')

            if ok:
                OUT_RASTERS = dict()
                for parameter in alg.outputDefinitions():
                    if isinstance(parameter, QgsProcessingOutputRasterLayer):
                        lyr = QgsRasterLayer(results[parameter.name()])
                        if not lyr.isValid():
                            info = f'Unable to open {lyr.source()}'
                            self.log(info, isError=True)
                        else:
                            tmp = rasterArray(lyr)
                            nb, nl, ns = tmp.shape

                            path1 = parameters[parameter.name()]
                            target_field_name = SpectralProcessingRasterDestination.pathToFieldName(path1)
                            target_field_index = speclib.fields().lookupField(target_field_name)
                            if target_field_index == -1:
                                # create a new field

                                if nb > 1:
                                    # create spectral profile fields
                                    field: QgsField = SpectralLibraryUtils.createProfileField(target_field_name)
                                    if not speclib.dataProvider().supportedType(field):
                                        field = SpectralLibraryUtils.createProfileField(target_field_name,
                                                                                        encoding=ProfileEncoding.Text)
                                else:
                                    # create standard field
                                    field: QgsField = QgsField(name=target_field_name,
                                                               type=numpyToQgisDataType(tmp.dtype))
                                    if not speclib.dataProvider().supportedType(field):
                                        field = QgsField(name=target_field_name, type=Qgis.DataType.Float32)

                                speclib.beginEditCommand(f'Add field {field.name()}')
                                assert SpectralLibraryUtils.addAttribute(speclib, field)
                                speclib.endEditCommand()

                                # speclib.commitChanges(False)

                                target_field_index = speclib.fields().lookupField(target_field_name)

                            if target_field_index >= 0:
                                # if necessary, change editor widget type to SpectralProfile
                                target_field: QgsField = speclib.fields().at(target_field_index)
                                if nb > 0 and supports_field(target_field) and not is_profile_field(target_field):
                                    setup = QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, {})
                                    speclib.setEditorWidgetSetup(target_field_index, setup)
                                    target_field = speclib.fields().at(target_field_index)

                                OUT_RASTERS[parameter.name()] = (lyr, tmp, target_field)

                if len(OUT_RASTERS) > 0:
                    available_fids = speclib.allFeatureIds()
                    speclib.beginEditCommand('Add raster processing results')
                    # reload active features to include new fields
                    activeFeatures = list(speclib.getFeatures(activeFeatureIDs))
                    # write raster values to features
                    for parameterName, (lyr, tmp, target_field) in OUT_RASTERS.items():
                        self.log(f'Write values to field {target_field.name()}...')

                        spectralProperties = QgsRasterLayerSpectralProperties.fromRasterLayer(lyr)
                        wl = spectralProperties.wavelengths()
                        wlu = spectralProperties.wavelengthUnits()
                        bbl = spectralProperties.badBands()

                        # wavelength need to be defined for all bands
                        if any([w is None for w in wl]):
                            wl = None

                        # choose 1st wavelength unit for entire profile
                        for w in wlu:
                            if w not in [None, '']:
                                wlu = w

                        # no need to save a bad-band-list (bbl) if it is True for all bands (default)
                        if all([b == 1 for b in bbl]):
                            bbl = None

                        target_field: QgsField
                        target_field_index: int = speclib.fields().lookupField(target_field.name())

                        is_profile = is_profile_field(target_field)
                        for i, feature in enumerate(activeFeatures):
                            feature: QgsFeature
                            value = None
                            if is_profile:
                                pixel_profile = tmp[:, 0, i]
                                pdict = prepareProfileValueDict(x=wl,
                                                                xUnit=wlu,
                                                                y=pixel_profile,
                                                                bbl=bbl)
                                value = encodeProfileValueDict(pdict, target_field)
                            else:
                                value = float(tmp[0, 0, i])
                                if target_field.type() == QVariant.String:
                                    value = str(value)
                            assert speclib.changeAttributeValue(feature.id(), target_field_index, value)
                            # assert feature.setAttribute(target_field_index, value)

                    self.log(f'Update {len(activeFeatures)} features')
                    # for feature in activeFeatures:
                    #    assert speclib.updateFeature(feature)
                    speclib.endEditCommand()

                    # speclib.commitChanges(False)

        except AlgorithmDialogBase.InvalidParameterValue as ex1:
            # todo: focus on widget with missing input
            if fail_fast:
                raise ex1
            msg = f'Invalid Parameter Value: {ex1.parameter.name()}'
            self.log(msg, isError=True, escapeHtml=False)
            # self.tabWidget.setCurrentWidget(self.tabLog)
            self.highlightParameterWidget(ex1.parameter, ex1.widget)
        except AlgorithmDialogBase.InvalidOutputExtension as ex2:
            if fail_fast:
                raise ex2
            msg = f'Invalid Output Extension: {ex2.message}'
            self.log(msg, isError=True, escapeHtml=False)
        except Exception as ex3:
            if fail_fast:
                raise ex3
            msg = f'{ex3}'
            self.log(msg, isError=True, escapeHtml=False)
            mbar: QgsMessageBar = self.messageBar()
            if isinstance(mbar, QgsMessageBar):
                mbar.pushMessage(msg, level=Qgis.MessageLevel.Critical)
        self.log('Done')
        self.processingFeedback().setProgress(int(100))

    def temporaryRaster(self) -> typing.List[str]:
        """
        Returns a list of all files which have been written by writeTemporaryRaster
        when calling runAlgorithm()
        """
        return self.mTemporaryRaster[:]

    def writeTemporaryRaster(self, dp: QgsRasterDataProvider, file_name, rasterblockFeedback, transformContext):

        file_writer = QgsRasterFileWriter(file_name)

        assert dp.xSize() > 0
        assert dp.ySize() > 0
        assert dp.bandCount() > 0

        pipe = QgsRasterPipe()
        if not pipe.set(dp):
            self.log(f'Cannot set pipe provider to write {file_name}', isError=True)
        else:
            self.log(f'Write {file_name}')
        error = file_writer.writeRaster(
            pipe,
            dp.xSize(),
            dp.ySize(),
            dp.extent(),
            dp.crs(),
            transformContext,
            rasterblockFeedback
        )

        del file_writer
        if error != QgsRasterFileWriter.WriterError.NoError:
            errMsg = LUT_RASTERFILEWRITER_ERRORS.get(error, 'unknown')
            raise Exception(f'Unable to write {file_name}\n'
                            f'QgsRasterFileWriterError: {errMsg}')

        # write additional metadata
        if isinstance(dp, VectorLayerFieldRasterDataProvider):
            fieldConverter: FieldToRasterValueConverter = dp.fieldConverter()
            field: QgsField = fieldConverter.field()
            if isinstance(fieldConverter, SpectralProfileValueConverter):
                # write spectral properties like wavelength per band
                fieldConverter.spectralSetting().writeToLayer(file_name)
            elif fieldConverter.isClassification():
                # set a categorical raster renderer with class names and colors
                layer: QgsRasterLayer = qgsRasterLayer(file_name)
                colorTable = fieldConverter.colorTable(1)
                classData = QgsPalettedRasterRenderer.colorTableToClassData(colorTable)
                renderer = QgsPalettedRasterRenderer(layer.dataProvider(), 1, classData)
                layer.setRenderer(renderer)
                layer.saveDefaultStyle(QgsMapLayer.StyleCategory.AllStyleCategories)
                del layer, renderer

        self.mTemporaryRaster.append(file_name)

    def messageBar(self) -> QgsMessageBar:
        return self.mProcessingWidgetContext.messageBar()

    def log(self, text, showLogPanel: bool = False, isError: bool = False, escapeHtml: bool = False):
        self.setInfo(text, isError=isError, escapeHtml=escapeHtml)
        if isError or showLogPanel:
            self.showLog()

    def highlightParameterWidget(self, parameter, widget):
        self.showParameters()

        wrapper: SpectralProcessingModelCreatorAlgorithmWrapper = self.processingModelWrapper()
        if isinstance(wrapper, SpectralProcessingModelCreatorAlgorithmWrapper):
            css = widget.styleSheet()
            widget.setStyleSheet('background-color: rgba(255, 0, 0, 150);')
            QTimer.singleShot(1000, lambda *args, w=widget, c=css: w.setStyleSheet(c))

    def createProcessingParameters(self, flags=None):
        if flags is None and Qgis.versionInt() >= 32400:
            flags = QgsProcessingParametersGenerator.Flags()

        if self.mainWidget() is None:
            return {}

        try:
            return self.mainWidget().createProcessingParameters(flags)
        except AlgorithmDialogBase.InvalidParameterValue as e:
            self.flag_invalid_parameter_value(e.parameter.description(), e.widget)
        except AlgorithmDialogBase.InvalidOutputExtension as e:
            self.flag_invalid_output_extension(e.message, e.widget)
        return {}

    def setAlgorithm(self, alg: typing.Union[str, pathlib.Path, QgsProcessingAlgorithm]):

        if isinstance(alg, str):
            reg: QgsProcessingRegistry = QgsApplication.instance().processingRegistry()
            a = reg.algorithmById(alg)
            if isinstance(a, QgsProcessingAlgorithm):
                alg = a
            else:
                alg = pathlib.Path(alg)

        if isinstance(alg, pathlib.Path):
            assert alg.is_file(), f'Not a model file: {alg}'
            m = QgsProcessingModelAlgorithm()
            m.fromFile(alg.as_posix())
            alg = m

        assert isinstance(alg, QgsProcessingAlgorithm)

        super().setAlgorithm(alg.create())
        self.setWindowTitle(self.mDialogName)
        self.mAlg = alg
        w = self.getParametersPanel(alg, self)
        # mw = self.mainWidget()
        # if isinstance(mw, QWidget):
        #    mw.setParent(None)
        if isinstance(w, QgsPanelWidget):
            self.setMainWidget(w)
        # self.mProcessingModelWrapper = w
        self.mPanelWidget = w
        self.updateGui()

    def getParametersPanel(self, alg: QgsProcessingAlgorithm,
                           parent: QWidget) -> SpectralProcessingModelCreatorAlgorithmWrapper:
        if isinstance(self.mSpeclib, QgsVectorLayer):
            panel = SpectralProcessingModelCreatorAlgorithmWrapper(alg,
                                                                   self.mSpeclib,
                                                                   processingContext=self.mProcessingContext,
                                                                   )
        else:
            panel = QgsPanelWidget()
            panel.layout().addWidget(QLabel('Missing spectral library'))
        return panel

    def processingModelWrapper(self) -> SpectralProcessingModelCreatorAlgorithmWrapper:
        # return self.mProcessingModelWrapper
        return self.mPanelWidget

    def selectedFeaturesOnly(self) -> bool:
        return self.cbSelectedFeaturesOnly.isEnabled() and self.cbSelectedFeaturesOnly.isChecked()

    def setSpeclib(self, speclib: QgsVectorLayer):
        if isinstance(self.mSpeclib, QgsVectorLayer):
            self.mSpeclib.willBeDeleted.disconnect(self.close)

        assert isinstance(speclib, QgsVectorLayer)
        self.mSpeclib = speclib
        self.mSpeclib.willBeDeleted.connect(self.close)

    def updateGui(self):

        sl = self.speclib()
        if isinstance(sl, QgsVectorLayer):
            n = sl.selectedFeatureCount()
            self.cbSelectedFeaturesOnly.setEnabled(n > 0)
            self.cbSelectedFeaturesOnly.setText(f'Only process {n} selected features')

        self.tbAlgorithmName: QLineEdit

        alg: QgsProcessingAlgorithm = self.algorithm()
        hasAlg = isinstance(alg, QgsProcessingAlgorithm)
        if hasAlg:
            self.tbAlgorithmName.setStyleSheet('')
            css = ''
            # info = f'<b>{alg.displayName()}</b> "{alg.id()}"'
            info = f'{alg.displayName()} "{alg.id()}"'
            tooltip = f'Algorithm Name: {alg.name()}<br>Algorithm ID: {alg.id()}'
        else:
            css = 'color:"red";'
            info = tooltip = self.tbAlgorithmName.placeholderText()
        self.tbAlgorithmName.setStyleSheet(css)
        self.tbAlgorithmName.setText(info)
        self.tbAlgorithmName.setToolTip(tooltip)
        self.setWindowTitle(self.mDialogName)

    def speclib(self) -> QgsVectorLayer:
        return self.mSpeclib
