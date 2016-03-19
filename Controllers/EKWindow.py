from PyQt5.Qt import QSystemTrayIcon, QIcon, QAction, QDialog, QMenu, \
    qApp, QFileDialog, QFileInfo, QTableWidgetItem, QAbstractItemView, QTableView, QSettings
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from view import dialog_ui
from database import DatabaseManager
from EkEngine import Engine

import win32api
import win32con
import os
import shutil
import time


class EKWindow(QDialog, dialog_ui.Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self)
        self.app_path = os.getenv("APPDATA") + "\\" + qApp.applicationName()
        self.registrySettings = QSettings("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run", QSettings.NativeFormat)
        self.table_path = self.app_path + "\\tables"
        self.engine = Engine()
        self.minimize_action = QAction("Minimize", self)
        self.maximize_action = QAction("Maximize", self)
        self.settings_action = QAction("Settings", self)
        self.about_action = QAction("About", self)
        self.quit_action = QAction("Quit", self)
        self.tray_icon_menu = QMenu(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.setupUi(self)
        self.icon = QIcon(QPixmap(":icon/off_logo"))
        self.construct_tray_icon()
        self.signal_connectors()
        self.database = DatabaseManager()
        self.shortcut_key = self.database.get_shortcut_key()
        self.populate_modifier_cbox()
        if self.database.get_current_state() == "True":
            self.engine.conv_state = False
        else:
            self.engine.conv_state = True
        self.icon_activated(QSystemTrayIcon.Trigger)
        self.file_path_tview.setEnabled(False)
        self.check_app_path()
        self.update_table(True)
        self.init_combobox()
        if self.registrySettings.contains(qApp.applicationName()):
            self.start_windows_check.setChecked(True)
        else:
            self.start_windows_check.setChecked(False)

    def check_app_path(self):
        if not os.path.exists(self.app_path):
            os.makedirs(self.app_path)
        if not os.path.exists(self.table_path):
            os.makedirs(self.table_path)
        return

    def construct_tray_icon(self):
        self.tray_icon.setIcon(self.icon)
        self.tray_icon_menu.addAction(self.settings_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.about_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()

    def signal_connectors(self):
        self.settings_action.triggered.connect(self.show_setting)
        self.about_action.triggered.connect(self.show_about)
        self.quit_action.triggered.connect(self.quit)
        self.add_new_button.clicked.connect(self.change_dialog_index)
        self.back_button.clicked.connect(self.change_dialog_index)
        self.modifier_cbox.currentIndexChanged.connect(self.populate_shortcut_key)
        self.shortcut_key_cbox.currentIndexChanged.connect(self.save_shortcut_key)
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.add_button.clicked.connect(self.save_file)
        self.clear_button.clicked.connect(self.reset_form)
        self.remove_button.clicked.connect(self.remove_keyboard)
        self.keyboard_cbox.currentIndexChanged.connect(self.save_current_keyboard)
        self.start_windows_check.stateChanged.connect(self.change_start_windows)

    def reset_form(self):
        self.clear_file_error()
        self.file_path_tview.setText("")

    def open_file_dialog(self):
        file_dialog = QFileDialog()
        self.file_path_tview.setText(QFileDialog.getOpenFileName(file_dialog,
                                                                 str("Choose  a SCIM Table"),
                                                                 "",
                                                                 str("Scim Tables (*.in *.txt)"))[0])

    def validate(self):
        try:
            with open(str(self.file_path_tview.text()), encoding="utf-8") as search:
                for line in search:
                    line = line.rstrip()  # remove '\n' at end of line
                    if "SCIM_Generic_Table_Phrase_Library_TEXT" in line:
                        return True
            self.show_file_error("Invalid SCIM Table file")
            return False
        except:
            self.show_file_error("Some error occurred")
            return False

    def save_file(self):
        if self.validate():
            self.clear_file_error()
            filepath = str(self.file_path_tview.text())
            fileinfo = QFileInfo(filepath)
            filename = str(int(time.time())) + "_" + fileinfo.fileName()
            keyboard_name = "Unknown"
            with open(filepath, encoding="utf-8") as search:
                for line in search:
                    line = line.rstrip()  # remove '\n' at end of line
                    if "NAME" in line:
                        name_line = line
                        name_list = name_line.split('=', 1)
                        if len(name_list) > 0:
                            keyboard_name = name_list[1]
            if keyboard_name == "Unknown":
                self.show_file_error("SCIM table name header not found")
            elif DatabaseManager.check_keyboard_exist(keyboard_name):
                self.show_file_error("Keyboard already exists")
            else:
                shutil.copyfile(filepath, self.table_path + "\\" + filename)
                DatabaseManager.add_keyboard(keyboard_name, filename)
                self.file_path_tview.setText("")
                self.update_table()

    def show_file_error(self, message):
        self.error_msg.setText(message)

    def clear_file_error(self):
        self.error_msg.setText("")

    def show_about(self):
        pass

    def quit(self):
        self.engine.un_hook()
        win32api.PostThreadMessage(win32api.GetCurrentThreadId(), win32con.WM_QUIT, 0, 0)
        self.exit(0)

    def show_setting(self):
        self.stacked_widget.setCurrentIndex(0)
        self.showNormal()

    def change_dialog_index(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            self.reset_form()
            self.init_table()
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.init_combobox()
            self.stacked_widget.setCurrentIndex(0)

    def populate_modifier_cbox(self):
        self.modifier_cbox.blockSignals(True)
        modifiers = DatabaseManager.get_keys()
        for modifier in modifiers:
            self.modifier_cbox.addItem(modifier.name, modifier.id)
            if modifier.id == self.shortcut_key.parent.id:
                self.modifier_cbox.setCurrentText(modifier.name)
        self.populate_shortcut_key()
        self.modifier_cbox.blockSignals(False)

    def populate_shortcut_key(self):
        self.shortcut_key_cbox.blockSignals(True)
        self.shortcut_key_cbox.clear()
        keys = DatabaseManager.get_keys(self.modifier_cbox.currentData())
        for key in keys:
            self.shortcut_key_cbox.addItem(key.name, key.id)
            if key.id == self.shortcut_key.id:
                self.shortcut_key_cbox.setCurrentText(key.name)
        self.shortcut_key_cbox.blockSignals(False)
        self.save_shortcut_key()

    def save_shortcut_key(self):
        DatabaseManager.set_shortcut_key(self.shortcut_key_cbox.currentData())
        self.shortcut_key = DatabaseManager.get_shortcut_key()
        self.register_shortcut_listener()

    def register_shortcut_listener(self):
        self.engine.event_queue.remove_all()
        if self.shortcut_key.parent.name == "NONE":
            self.engine.event_queue.register_event(
                [
                    [self.shortcut_key.name],
                    self.icon_activated,
                    QSystemTrayIcon.Trigger
                ]
            )
        elif self.shortcut_key.parent.name == "CTRL":
            self.engine.event_queue.register_event(
                [
                    ['Lcontrol', self.shortcut_key.name],
                    self.icon_activated,
                    QSystemTrayIcon.Trigger
                ]
            )
            self.engine.event_queue.register_event(
                [
                    ['Rcontrol', self.shortcut_key.name],
                    self.icon_activated,
                    QSystemTrayIcon.Trigger
                ]
            )
        elif self.shortcut_key.parent.name == "ALT":
            self.engine.event_queue.register_event(
                [
                    ['LMenu', self.shortcut_key.name],
                    self.icon_activated,
                    QSystemTrayIcon.Trigger
                ]
            )
            self.engine.event_queue.register_event(
                [
                    ['RMenu', self.shortcut_key.name],
                    self.icon_activated,
                    QSystemTrayIcon.Trigger
                ]
            )
        return True

    def change_status(self):
        self.engine.conv_state = not self.engine.conv_state
        DatabaseManager.set_current_state(self.engine.conv_state)
        if self.engine.conv_state:
            self.show_on_status()
            self.load_keyboard()
        else:
            self.show_off_status()

    def icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            pass
        elif reason == QSystemTrayIcon.Trigger:
            self.change_status()
        elif reason == QSystemTrayIcon.MiddleClick:
            pass
        else:
            pass

    def show_on_status(self):
        self.icon = QIcon(QPixmap(":icon/on_logo"))
        self.change_icons()

    def show_off_status(self):
        self.icon = QIcon(QPixmap(":icon/off_logo"))
        self.change_icons()

    def change_icons(self):
        self.tray_icon.setIcon(self.icon)
        self.setWindowIcon(self.icon)
        # TODO : Need to implement this method with current keyboard name
        self.tray_icon.setToolTip("Keyboard Name")
        self.show_tray_message()

    def show_tray_message(self):
        if self.engine.conv_state:
            message = "Ekalappai is Switched ON"
        else:
            message = "Ekalappai is Switched OFF"
        self.tray_icon.showMessage(
            qApp.applicationName() + " " + qApp.applicationVersion(),
            message,
            QSystemTrayIcon.MessageIcon(0),
            100
        )

    def update_table(self, init=False):
        if init:
            self.init_table()
        records = DatabaseManager.get_all_keyboards()
        self.keyboard_table.setRowCount(records[0])
        for idx, record in enumerate(records[1]):
            self.keyboard_table.setItem(idx, 1, QTableWidgetItem(record.language_name))
            self.keyboard_table.setItem(idx, 2, QTableWidgetItem(str(record.id)))
            chk_box = QTableWidgetItem()
            chk_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_box.setCheckState(Qt.Unchecked)
            self.keyboard_table.setItem(idx, 0, chk_box)
        self.keyboard_table.resizeRowsToContents()
        return

    """
        Initialize the grid with the default options
    """
    def init_table(self):
        self.keyboard_table.setColumnCount(3)
        self.keyboard_table.setHorizontalHeaderLabels(["", "Name", "Id"])
        self.keyboard_table.setColumnHidden(2, True)
        self.keyboard_table.setColumnWidth(0, 30)
        self.keyboard_table.horizontalHeader().setStretchLastSection(True)
        self.keyboard_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.keyboard_table.setSelectionBehavior(QTableView.SelectRows)
        self.keyboard_table.setSelectionMode(QAbstractItemView.SingleSelection)

    def remove_keyboard(self):
        for row in range(0, self.keyboard_table.rowCount()):
            if self.keyboard_table.item(row, 0).checkState() == Qt.Checked and \
                            DatabaseManager.get_current_keyboard() != self.keyboard_table.item(row, 2).text():
                DatabaseManager.remove_keyboard(int(self.keyboard_table.item(row, 2).text()))
        self.update_table()

    def init_combobox(self):
        self.keyboard_cbox.blockSignals(True)
        self.keyboard_cbox.clear()
        current_keyboard = DatabaseManager.get_current_keyboard()
        index = 0
        for keyboard in DatabaseManager.get_all_keyboards()[1]:
            self.keyboard_cbox.addItem(keyboard.language_name, keyboard.id)
            if int(current_keyboard) == keyboard.id:
                self.keyboard_cbox.setCurrentText(keyboard.language_name)
                self.keyboard_cbox.setCurrentIndex(index)
            index += 1
        self.keyboard_cbox.blockSignals(False)

    def save_current_keyboard(self):
        DatabaseManager.set_current_keyboard(self.keyboard_cbox.currentData())
        self.engine.conv_state = True
        DatabaseManager.set_current_state(self.engine.conv_state)
        self.show_on_status()
        self.load_keyboard()

    def load_keyboard(self):
        self.engine.file_name = self.table_path +\
                                "\\" + \
                                DatabaseManager.get_keyboard_path(DatabaseManager.get_current_keyboard())
        self.engine.initialize()

    def change_start_windows(self):
        if self.start_windows_check.isChecked():
            self.registrySettings.setValue(qApp.applicationName(), qApp.applicationFilePath())
        else:
            self.registrySettings.remove(qApp.applicationName())
