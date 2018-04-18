# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveLayerInGeoDASH
                                 A QGIS plugin
 This plugin saves layer in GeoDASH from qgis
                              -------------------
        begin                : 2018-04-16
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Jahangir Alam
        email                : jahangir.cse09@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
from nbformat.v2.nbxml import _set_text

from PyQt4.QtGui import QMessageBox, QWidget, QLineEdit

import resources
# Import the code for the dialog
from save_layer_geodash_plugin_dialog import SaveLayerInGeoDASHDialog
import os.path
import requests
import zipfile

import json
import shutil
import tempfile
from shutil import copyfile

host = "http://localhost:8000/"

class SaveLayerInGeoDASH:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaveLayerInGeoDASH_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SaveLayerInGeoDASHDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Save Layer in GeoDASH')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SaveLayerInGeoDASH')
        self.toolbar.setObjectName(u'SaveLayerInGeoDASH')

        self.dlg.password.clear()
        self.dlg.uploadButton.clicked.connect(self.uploadLayer)



    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SaveLayerInGeoDASH', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SaveLayerInGeoDASH/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Save Layer in GeoDASH'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Save Layer in GeoDASH'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        self.initializeDialog()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # self.printme0()
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass



    def initializeDialog(self):
        """
            Created by: Jahangir Alam
            jahangir.cse09@gmail.com
            github: jahangir091

        This method initializes primary data to the
        fields in the plugin. Fetches organization list and
        categories and showes loaded layers to qgis.

        Also sets placeholder for some fields and clears cache data from comboboxes.

        :return:
        """

        # List all the layers loaded in qgis
        layers = self.iface.legendInterface().layers()
        layer_list = []

        #clear selectLayer combobox
        self.dlg.selectLayer.clear()

        self.dlg.password.setEchoMode(QLineEdit.Password)

        #list all the layers loaded in qgis
        #which contains .shp extension
        for layer in layers:
            if layer.source().endswith('.shp'):
                layer_list.append(layer.name())

        #add layer list to selectLayer combobox
        self.dlg.selectLayer.addItems(layer_list)

        #get available categories from geodash server
        response = requests.get(host + "api/categories/")
        categories = []

        #clear select category combobox
        self.dlg.selectCategory.clear()
        for cat in response.json()['objects']:
            categories.append(cat['gn_description'])

        #add categories to selectCategory combobox
        self.dlg.selectCategory.addItems(categories)


        #get available organizations from geodash
        response = requests.get(host + "api/groups/")
        organizations = []

        #clear selectOrganization combobox before initialization
        self.dlg.selectOrganization.clear()
        for org in response.json()['objects']:
            organizations.append(org['title'])

        #add organizations to selectOrganization combobox
        self.dlg.selectOrganization.addItems(organizations)

        # add placeholder for host and layer title field
        self.dlg.host.setPlaceholderText("https://geodash.gov.bd/")  # setPlaceholderText("Don't mind me.")
        self.dlg.layerTitle.setPlaceholderText("Give a title to your layer")  # setPlaceholderText("Don't mind me.")



    def uploadLayer(self):
        """
            Created by: Jahangir Alam
            jahangir.cse09@gmail.com
            github: jahangir091

        :return:
        """

        host = self.dlg.host.text()

        #loaded layer list in qgis
        layers = self.iface.legendInterface().layers()

        #layer index that is selected from the combo box
        selectedLayerIndex = self.dlg.selectLayer.currentIndex()
        selectedLayer = layers[selectedLayerIndex]
        #name of the selected layer
        selectedLayerName = selectedLayer.name()

        #find the path where the layer is in the disk
        layerDirectorypath = selectedLayer.dataProvider().dataSourceUri()
        layerDirectory, fileName = os.path.split(layerDirectorypath)


        #this method checks if mandatory inputs are given or not
        # if not, show error message
        displayErrorMessage = self.checkInputFields()

        if displayErrorMessage != '':
            w = QWidget()
            QMessageBox.warning(w, 'message', displayErrorMessage)

        elif not os.path.exists(layerDirectory):
            # if selected layer directory can not be found, show error message
            displayErrorMessage = "Can not find layer directory"
            w = QWidget()
            QMessageBox.warning(w, 'message', displayErrorMessage)

        else:
            filesInDirectory = os.listdir(layerDirectory)
            tmp_dir = tempfile.mkdtemp()

            requiredFilesList = []
            for f in filesInDirectory:
                if f == selectedLayerName + '.shp':
                    shapeFilePath = layerDirectory + '/' + selectedLayerName + '.shp'
                    copyfile(shapeFilePath, tmp_dir + "/" + f)
                    requiredFilesList.append('.shp')
                elif f == selectedLayerName + '.shx':
                    shxFilePath = layerDirectory + '/' + selectedLayerName + '.shx'
                    copyfile(shxFilePath, tmp_dir + "/" + f)
                    requiredFilesList.append('.shx')
                elif f == selectedLayerName + '.prj':
                    prjFilePath = layerDirectory + '/' + selectedLayerName + '.prj'
                    copyfile(prjFilePath, tmp_dir + "/" + f)
                    requiredFilesList.append('.prj')
                elif f == selectedLayerName + '.dbf':
                    dbfFilePath = layerDirectory + '/' + selectedLayerName + '.dbf'
                    copyfile(dbfFilePath, tmp_dir + "/" + f)
                    requiredFilesList.append('.dbf')
                else:
                    # implement error handling here
                    pass

            msg = ''
            if '.shp' not in requiredFilesList:
                msg = "missing .shp file"
            if '.shx' not in requiredFilesList:
                msg = "missing .shx file"
            if '.prj' not in requiredFilesList:
                msg = "missing .prj file"
            if '.dbf' not in requiredFilesList:
                msg = "missing .dbf file"

            if msg != '':
                displayErrorMessage = "Layer directory is" + msg
                w = QWidget()
                QMessageBox.warning(w, 'message', displayErrorMessage)
            else:
                with zipfile.ZipFile(tmp_dir + '/' + selectedLayerName + '.zip', 'w') as myzip:
                    myzip.write(shapeFilePath)
                    myzip.write(shxFilePath)
                    myzip.write(prjFilePath)
                    myzip.write(dbfFilePath)
                myzip.close()

                file_path = myzip.filename

                data = {}
                data["username"] = self.dlg.username.text()
                data["password"] = self.dlg.password.text()
                data["layer_title"] = self.dlg.layerTitle.text()
                data["category"] = self.dlg.selectCategory.currentText()
                data["organization"] = 1  # self.dlg.selectOrganization.text()
                data["charset"] = "UTF-8"

                permission_json = {}
                permission_json['users'] = {"AnonymousUser": ["view_resourcebase", "download_resourcebase"],
                                            "admin": ["change_layer_data"]}
                permission_json['groups'] = {"default": ["change_layer_data"]}
                json_data = json.dumps(permission_json)

                data[
                    "permissions"] = json_data  # {"users":{"AnonymousUser":["view_resourcebase","download_resourcebase"],"admin":["change_layer_data"]},"groups":{"default":["change_layer_data"]}}

                files = {"base_file": open(file_path, 'rb')}

                data["base_file"] = layerDirectory

                request_url = host + "api/layerupload/"
                response = requests.post(request_url, files=files, data=data)

                w = QWidget()
                if response.status_code == 200:
                    mss = QMessageBox()
                    mss.setIcon(QMessageBox.Information)
                    mss.warning(w, 'message', "Uploaded layer successfully")
                else:
                    QMessageBox.warning(w, 'message', response.json()['error_message'])


    def checkInputFields(self):
        if not self.dlg.username.text():
            return "username field is required"
        if not self.dlg.password.text():
            return "password field is required"
        if not self.dlg.host.text():
            return "host url field is required"
        if not self.dlg.layerTitle.text():
            return "layer title field is required"

        return ''