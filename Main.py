import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QTranslator, QDir, QPoint, QMimeData, QRect, Qt
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QMenuBar, QActionGroup, QDialog, QLabel, \
    QTableView, QAbstractItemView, QHeaderView, QVBoxLayout, QPushButton

from managers import js_manager
from models.EdgePropertyModel import EdgePropertyModel
from models.NodePropertyModel import NodePropertyModel
from ui.Ui_DlgEdge import Ui_DlgEdge
from ui.Ui_MainWindow import Ui_MainWindow


class DlgEdge(QDialog):
    graphView = None

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_DlgEdge()
        self.ui.setupUi(self)

        self.ui.cboRelationType.addItem("Confirmed")
        self.ui.cboRelationType.addItem("Suspeted")

    def showEvent(self, arg1):
        self.ui.cboSource.clear()
        self.ui.txtLabel.setText("")
        self.ui.txtWeight.setText("0")
        #self.ui.cboSource.addItems(graphm.G.nodes())
        self.ui.cboTarget.clear()
        #self.ui.cboTarget.addItems(graphm.G.nodes())

    def accept(self):
        source = self.ui.cboSource.currentText()
        target = self.ui.cboTarget.currentText()
        label = self.ui.txtLabel.text()
        weight = float(self.ui.txtWeight.text())
        self.graphView.add_edge(source, target, label, weight)

        super().accept()


class GraphView(QMainWindow):
    selectedPoints = []

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #js_manager.node_updated.connect(self.ui.graphView.apply_settings)

        self.dlgedge = DlgEdge(self)
        self.dlgedge.graphView = self.ui.graphView

        self.setAcceptDrops(True)
        self.dragStartPosition = QPoint()

        #self._load_state()
        self._read_json()
        self.__init_property_view()

    def _read_json(self):
        js_manager.init(file_name="type.json")
        self.toolbox = js_manager.tool_box_widget(parent=self.ui.dockWidgetContents_4)
        self.ui.verticalLayout_8.addWidget(self.toolbox)

    def __init_property_view(self):
        self.tableView = QTableView(self.ui.dockWidgetContents_2)
        self.tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.node_property_model = NodePropertyModel(self.tableView)
        self.node_property_model.dataChanged.connect(self.__node_property_changed)
        js_manager.node_updated.connect(self.node_property_model.reset)
        self.edge_property_model = EdgePropertyModel(self.tableView)
        self.edge_property_model.dataChanged.connect(self.__edge_property_changed)
        v_layout = QVBoxLayout(self.ui.dockWidgetContents_2)
        v_layout.addWidget(self.tableView)
        self.remove_button = QPushButton("", self.ui.dockWidgetContents_2)
        self.remove_button.setText(self.tr("Delete"))
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.__remove_selected)
        v_layout.addWidget(self.remove_button)

    def __node_property_changed(self):
        self.ui.graphScene.apply_settings()

    def __edge_property_changed(self):
        self.ui.graphScene.apply_settings()

    def __remove_selected(self):
        # nodes = list(graphm.cur_G.nodes.data(False))
        # for i in self.ui.graphView.selected_node_indexes:
        #     graphm.G.remove_node(nodes[i])
        #
        # edges = list(graphm.cur_G.edges.data(False))
        # for i in self.ui.graphView.edge_selected_indexes:
        #     graphm.G.remove_edge(edges[i][0], edges[i][1])
        #
        # self.ui.graphView.selected_node_indexes = []
        # self.ui.graphView.edge_selected_indexes = []
        #
        # self.ui.graphView.selected_node_names = None
        # self.ui.graphView.selected_node_pressed_positions = None
        self.__deselected()
        self.apply_settings()
    def apply_settings(self):
        self.ui.graphScene.style_updated = True
        if self.graph_layout_has_changed:
            # self.ui.graphView.apply_settings(graphm.G.graph["g_type"])
            self.graph_layout_has_changed = False
        else:
            self.ui.graphScene.apply_settings()

class MainView(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.license_file = ""
        self.translator = None

        self.tabWidget = QTabWidget()
        self.graph_view = GraphView()
        self.tabWidget.addTab(self.graph_view, self.tr("Graph"))
        self.tabWidget.addTab(QWidget(), self.tr("Timeline"))
        self.setCentralWidget(self.tabWidget)

        self.menubar = QMenuBar()
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menu_file_items = self.menubar.addMenu("&File")
        self.menu_file_items.aboutToShow.connect(self.on_menu_file_about_to_show)

        self.menu_language_items = self.menubar.addMenu("&Language")
        self.menu_language_items.aboutToShow.connect(
            self.on_menu_language_about_to_show
        )
        self.menu_language_items_group = QActionGroup(self)
        self.menu_language_items_group.setExclusive(True)

        self.menu_help_items = self.menubar.addMenu("&Help")
        self.menu_help_items.aboutToShow.connect(self.on_menu_help_about_to_show)

    def on_menu_file_about_to_show(self):
        self.menu_file_items.clear()
        action = self.menu_file_items.addAction("")
        action.setText(self.tr("&New"))
        #action.triggered.connect(self.graph_view.clear_graph)
        action = self.menu_file_items.addAction("")
        action.setText(self.tr("&Open..."))
        #action.triggered.connect(self.graph_view.open_graph)
        action = self.menu_file_items.addAction("&Import...")
        action.setText(self.tr("&Import..."))
        action.setDisabled(True)
        action = self.menu_file_items.addAction("&Close")
        action.setText(self.tr("&Close"))
        action.setDisabled(True)
        action = self.menu_file_items.addAction("&Save...")
        action.setText(self.tr("&Save..."))
        #action.triggered.connect(self.graph_view.save_graph)
        action = self.menu_file_items.addAction("&Export Image...")
        action.setText(self.tr("&Export Image..."))
        #action.triggered.connect(self.graph_view.export_image)

        action = self.menu_file_items.addAction("&Exit")
        action.setText(self.tr("&Exit"))
        action.triggered.connect(self.exit)

    def on_menu_language_about_to_show(self):
        self.menu_language_items.clear()

        actions = self.menu_language_items_group.actions()
        for action in actions:
            self.menu_language_items_group.removeAction(action)

        action = self.menu_language_items.addAction("")
        action.setText(self.tr("&English"))
        self.menu_language_items_group.addAction(action)
        action.setCheckable(True)
        action.setChecked(self.translator is None)
        action.triggered.connect(lambda: self.on_language_changed(""))

        action = self.menu_language_items.addAction("")
        action.setText(self.tr("&Russian"))
        self.menu_language_items_group.addAction(action)
        action.setCheckable(True)
        action.setChecked(self.translator is not None and self.translator.language() == "ru_RU")
        action.triggered.connect(lambda: self.on_language_changed("RU"))

    def on_language_changed(self, language: str):
        QDir.addSearchPath("translations", "translations")
        if language == "RU":
            self.translator = QTranslator(self)
            if self.translator.load(u"RU.qm", ":/translations"):
                QApplication.installTranslator(self.translator)
        else:
            if self.translator:
                QApplication.removeTranslator(self.translator)
            self.translator = None

        self.graph_view.ui.retranslateUi(self.graph_view)

        self.menu_file_items.setTitle(self.tr("&File"))
        self.menu_language_items.setTitle(self.tr("&Language"))
        self.menu_help_items.setTitle(self.tr("&Help"))

        self.tabWidget.setTabText(0, self.tr("Graph"))
        self.tabWidget.setTabText(1, self.tr("Timeline"))

        self.graph_view.dlgedge.ui.retranslateUi(self.graph_view.dlgedge)
        for ind in range(self.graph_view.toolbox.count()):
            self.graph_view.toolbox.setItemText(ind, self.tr(self.graph_view.toolbox.itemText(ind)))

        self.graph_view.remove_button.setText(self.tr('Delete'))

    def on_menu_help_about_to_show(self):
        self.menu_help_items.clear()
        action = self.menu_help_items.addAction("")
        action.setText(self.tr("&About"))
        #action.triggered.connect(self.show_about_dialog)

    def exit(self):
        QApplication.closeAllWindows()

    # def show_about_dialog(self) -> None:
    #     ShowLicenseWindow = Ui_Registration()
    #     ShowLicenseWindow.aboutLicense(self.license_file)
    #     ShowLicenseWindow.exec_()


app = QApplication([])
mainwindow = MainView()
mainwindow.show()
sys.exit(app.exec_())
# END: bypass license check


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    app.setOrganizationName("Graph")
    app.setApplicationName("Graph")

    # check license file
    licenseFlag = False

    for licenseFile in glob.glob("*.license"):
        if check_license_file(licenseFile):
            licenseFlag = True
            file = licenseFile

    if licenseFlag:
        mainwindow = MainView()
        mainwindow.license_file = file
        mainwindow.show()
    else:
        print("License is expired or not found.")
        addLicenseWindow = Ui_Registration()
        result = addLicenseWindow.exec_()
        if result == 0:
            sys.exit(0)

        if len(addLicenseWindow.licenseFile) > 0:
            print(
                'License file: "'
                + addLicenseWindow.licenseFile
                + '" is copied to current folder.'
            )

            old_path, base = os.path.split(addLicenseWindow.licenseFile)
            new_path = os.path.join(os.getcwd(), base)
            dest = shutil.copyfile(addLicenseWindow.licenseFile, new_path)

            if check_license_file(dest):
                mainwindow = MainView()
                mainwindow.license_file = base
                mainwindow.show()

    sys.exit(app.exec_())