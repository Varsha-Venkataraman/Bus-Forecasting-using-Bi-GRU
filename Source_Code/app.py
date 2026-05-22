import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFormLayout, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox, QHeaderView,
    QDialog, QSpinBox, QDateEdit, QCalendarWidget
)
from PySide6.QtCore import Qt, QObject, QThread, Signal, QDate

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

import bus_ops
import driver_ops
import prediction

def create_calendar_field(min_years=0, max_years=10):
    date_field = QDateEdit()
    date_field.setCalendarPopup(True)
    date_field.setDisplayFormat("dd-MM-yyyy")

    today = QDate.currentDate()
    date_field.setMinimumDate(today.addYears(min_years))
    date_field.setMaximumDate(today.addYears(max_years))

    calendar = date_field.calendarWidget()
    calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
    calendar.setMinimumWidth(350)

    return date_field

class PredictionWorker(QObject):
    finished = Signal(object, object)
    error = Signal(str)

    def __init__(self, bus_id, filepath='bus_data.csv'):
        super().__init__()
        self.bus_id = bus_id
        self.filepath = filepath

    def run(self):
        try:
            preds, fig = prediction.run_bus_prediction(
                bus_id=self.bus_id,
                filepath=self.filepath
            )
            self.finished.emit(preds, fig)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Management")
        self.setGeometry(200, 100, 1200, 700)

        # --- NAVIGATION TABS ---
        self.tabs = QTabWidget()
        self.tabs.addTab(self.dashboard_tab(), "Home")
        self.tabs.addTab(self.bus_tab(), "Bus Management")
        self.tabs.addTab(self.driver_tab(), "Driver Management")

        self.setCentralWidget(self.tabs)

        # --- STATE VARIABLES ---
        self.selected_bus_id = None
        self.selected_driver_id = None

        # --- Apply Styling ---
        theme_colors = {
            "primary": "#2E86AB",     # Elegant teal-blue
            "secondary": "#1B4965",   # Deep navy for contrast
            "ternary": "#EEF3F7",      # Close to backgroud
            "accent": "#5BC0EB",      # Soft aqua highlight
            "background": "#F9FAFB",  # Very light neutral background
            "alert": "#FF6F61",       # Coral for warnings
            "text": "#2E2E2E",        # Dark gray text
            "success": "#4CAF50",     # Green for confirm
            "danger": "#E53935",      # Red for delete
            "neutral": "#9E9E9E"      # Gray for reset
        }

        app.setStyleSheet(f"""
            QWidget {{
                background-color: {theme_colors['background']};
                font-family: 'Segoe UI', 'Roboto', Arial;
                color: {theme_colors['text']};
                font-size: 15px;
            }}

            /* Tabs */
            QTabWidget::pane {{
                border: none;
                background: white;
                border-radius: 12px;
                padding: 6px;
            }}
            QTabBar::tab {{
                background: {theme_colors['primary']};
                color: white;
                padding: 8px 16px;
                border-radius: 8px 8px 0 0;
                margin-right: 4px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {theme_colors['secondary']};
            }}
            QTabBar::tab:hover {{
                background: {theme_colors['accent']};
            }}

            /* Buttons */
            QPushButton {{
                background-color: {theme_colors['primary']};
                color: white;
                font-weight: 500;
                border-radius: 8px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                background-color: {theme_colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {theme_colors['secondary']};
            }}

            /* Group Boxes */
            QGroupBox {{
                background: #ffffff;
                border-radius: 12px;
                margin-top: 14px;
                padding: 14px;
                border: 1px solid #E0E0E0;
            }}
            QGroupBox::title {{
                color: {theme_colors['secondary']};
                font-weight: bold;
                font-size: 15px;
                padding: 6px;
            }}

            /* Tables */
            QTableWidget {{
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                selection-background-color: {theme_colors['primary']};
                selection-color: white;
            }}
            QHeaderView::section {{
                background-color: {theme_colors['ternary']};
                color: {theme_colors['secondary']};
                padding: 6px;
                border: none;
                font-weight: 600;
            }}

            /* Inputs */
            QLineEdit, QSpinBox, QDateEdit {{
                background: white;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }}
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {theme_colors['accent']};
            }}

            /* Dialogs */
            QDialog {{
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}

            /* Message Boxes */
            QMessageBox {{
                background-color: #ffffff;
                border-radius: 10px;
            }}
            QMessageBox QLabel {{
                color: {theme_colors['text']};
                font-size: 14px;
            }}

            /* Calendar */
            QCalendarWidget QAbstractItemView:enabled {{
                color: {theme_colors['text']};
                selection-background-color: {theme_colors['primary']};
                selection-color: white;
            }}

            /* Filter Section */
            QWidget#FilterBox {{
                background-color: {theme_colors['ternary']} ;
                border-radius: 10px;
                padding: 10px;
                margin: 8px 0;
                border: 1px solid #D0D8E0;
            }}
            QWidget#FilterBox QLabel {{
                color: {theme_colors['secondary']};
                font-size: 13px;
                font-weight: 500;
            }}
            QWidget#FilterBox QLineEdit,
            QWidget#FilterBox QSpinBox,
            QWidget#FilterBox QDateEdit {{
                background: #ffffff;
                border: 1px solid #C0C0C0;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 13px;
            }}
            QWidget#FilterBox QPushButton {{
                background-color: {theme_colors['primary']};
                color: white;
                font-size: 13px;
                border-radius: 6px;
                padding: 4px 10px;
            }}

            QWidget#FilterBox QPushButton:hover {{
                background-color: {theme_colors['accent']};
            }}

            /* Dashboard Title */
            QLabel#DashboardTitle {{
                font-size: 28px;
                font-weight: bold;
                color: {theme_colors['primary']};
                margin: 20px;
            }}

            /* About Section Card */
            QGroupBox#AboutCard {{
                background: #ffffff;
                border: 1px solid #D0D8E0;
                border-radius: 12px;
                margin: 14px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
                color: {theme_colors['primary']};
            }}
            QGroupBox#AboutCard::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 4px 12px;
            }}

            /* About Text */
            QLabel#AboutText {{
                font-size: 14px;
                color: {theme_colors['secondary']};
                margin: 10px 20px;
            }}
        """)


        self.showMaximized()

    # --- DASHBOARD TAB ---
    def dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # --- Title ---
        title_label = QLabel("College Transport Management System")
        title_label.setObjectName("DashboardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # --- About Section Card ---
        about_card = QGroupBox("About the Project")
        about_card.setObjectName("AboutCard")
        about_layout = QVBoxLayout()

        about_label = QLabel("""
            College Transport Management System is a streamlined platform built to handle the everyday
            challenges of managing buses, drivers, and routes within a college environment. It provides an
            organized way to store and update records, ensuring that transport operations remain efficient
            and reliable. The system is designed with a clean interface and practical tools that make
            searching, adding, and updating information quick and intuitive.

            Beyond core management, the project also integrates a machine learning model that predicts bus
            demand for specific routes based on their IDs. This intelligent feature helps administrators
            anticipate usage patterns, allocate resources more effectively, and keep the transport network
            running smoothly with data‑driven insights.
            """)
        about_label.setObjectName("AboutText")
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignCenter)

        about_layout.addWidget(about_label)
        about_card.setLayout(about_layout)
        layout.addWidget(about_card)

        widget.setLayout(layout)
        return widget


    # --- BUS MANAGEMENT TAB ---
    def bus_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Search Section
        toggle_btn = QPushButton("Show Filters")
        layout.addWidget(toggle_btn)

        filter_box = QWidget()
        filter_box.setObjectName("FilterBox")
        search_layout = QFormLayout(filter_box)

        self.bus_id_search = QLineEdit()
        self.route_search = QLineEdit()
        self.bus_no_search = QLineEdit()
        self.license_search = QLineEdit()
        self.expiry_search = QLineEdit()
        self.capacity_search = QLineEdit()
        self.driver_search = QLineEdit()

        search_layout.addRow("Bus ID:", self.bus_id_search)
        search_layout.addRow("Route:", self.route_search)
        search_layout.addRow("Bus No:", self.bus_no_search)
        search_layout.addRow("License No:", self.license_search)
        search_layout.addRow("Expiry:", self.expiry_search)
        search_layout.addRow("Capacity:", self.capacity_search)
        search_layout.addRow("Driver ID:", self.driver_search)

        # --- Buttons row ---
        buttons_row = QHBoxLayout()
        search_btn = QPushButton("Search")
        clear_btn = QPushButton("Clear")

        search_btn.clicked.connect(self.search_buses)

        def clear_filters():
            self.bus_id_search.clear()
            self.route_search.clear()
            self.bus_no_search.clear()
            self.license_search.clear()
            self.expiry_search.clear()
            self.capacity_search.clear()
            self.driver_search.clear()

        clear_btn.clicked.connect(clear_filters)

        buttons_row.addWidget(search_btn)
        buttons_row.addWidget(clear_btn)

        search_layout.addRow(buttons_row)


        layout.addWidget(filter_box)
        filter_box.setVisible(False)   # search box initially collapsed

        def toggle_filters():
            visible = filter_box.isVisible()
            filter_box.setVisible(not visible)
            toggle_btn.setText("Hide Filters" if not visible else "Show Filters")

        toggle_btn.clicked.connect(toggle_filters)

        # Results Table
        self.bus_table = QTableWidget()
        self.bus_table.setColumnCount(7)
        self.bus_table.setHorizontalHeaderLabels(["ID", "Route", "Bus No", "License", "Expiry", "Capacity", "Driver ID"])
        self.bus_table.cellClicked.connect(self.select_bus)
        layout.addWidget(self.bus_table)

        self.bus_table.horizontalHeader().setStretchLastSection(True)
        self.bus_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bus_table.itemSelectionChanged.connect(self.clear_bus_selection)

        self.search_buses()

        # Actions
        actions_layout = QHBoxLayout()
        add_btn = QPushButton("Add Bus")
        add_btn.clicked.connect(self.add_bus)
        update_btn = QPushButton("Update Bus")
        update_btn.clicked.connect(self.update_bus)
        delete_btn = QPushButton("Delete Bus")
        delete_btn.clicked.connect(self.delete_bus)

        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(update_btn)
        actions_layout.addWidget(delete_btn)
        layout.addLayout(actions_layout)

        # Prediction Section
        pred_group = QGroupBox("Passenger Demand Prediction")
        pred_layout = QVBoxLayout()
        self.bus_id_input = QLineEdit()
        self.bus_id_input.setPlaceholderText("Enter Bus ID")
        pred_layout.addWidget(self.bus_id_input)

        self.pred_btn = QPushButton("Predict")
        self.pred_btn.clicked.connect(self.run_prediction_ui)
        pred_layout.addWidget(self.pred_btn)

        pred_group.setLayout(pred_layout)
        layout.addWidget(pred_group)

        widget.setLayout(layout)
        return widget


    # --- DRIVER MANAGEMENT TAB ---
    def driver_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # --- Search Section ---
        toggle_btn = QPushButton("Show Filters")
        layout.addWidget(toggle_btn)

        filter_box = QWidget()
        filter_box.setObjectName("FilterBox")
        search_layout = QFormLayout(filter_box)

        self.driver_id_search = QLineEdit()
        self.driver_name_search = QLineEdit()

        search_layout.addRow("Driver ID:", self.driver_id_search)
        search_layout.addRow("Driver Name:", self.driver_name_search)

        # --- Buttons row ---
        buttons_row = QHBoxLayout()
        search_btn = QPushButton("Search")
        clear_btn = QPushButton("Clear")

        search_btn.clicked.connect(self.search_drivers)

        def clear_driver_filters():
            self.driver_id_search.clear()
            self.driver_name_search.clear()

        clear_btn.clicked.connect(clear_driver_filters)

        buttons_row.addWidget(search_btn)
        buttons_row.addWidget(clear_btn)

        search_layout.addRow(buttons_row)

        layout.addWidget(filter_box)
        filter_box.setVisible(False)   # collapsed initially

        def toggle_filters():
            visible = filter_box.isVisible()
            filter_box.setVisible(not visible)
            toggle_btn.setText("Hide Filters" if not visible else "Show Filters")

        toggle_btn.clicked.connect(toggle_filters)

        # --- Results Table ---
        self.driver_table = QTableWidget()
        self.driver_table.setColumnCount(2)
        self.driver_table.setHorizontalHeaderLabels(["ID", "Name"])
        self.driver_table.cellClicked.connect(self.select_driver)
        layout.addWidget(self.driver_table)

        self.driver_table.horizontalHeader().setStretchLastSection(True)
        self.driver_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.driver_table.itemSelectionChanged.connect(self.clear_driver_selection)

        self.search_drivers()

        # Actions
        actions_layout = QHBoxLayout()
        add_btn = QPushButton("Add Driver")
        add_btn.clicked.connect(self.add_driver)
        update_btn = QPushButton("Update Driver")
        update_btn.clicked.connect(self.update_driver)
        delete_btn = QPushButton("Delete Driver")
        delete_btn.clicked.connect(self.delete_driver)

        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(update_btn)
        actions_layout.addWidget(delete_btn)
        layout.addLayout(actions_layout)

        widget.setLayout(layout)
        return widget

    # --- BUS FUNCTIONS ---
    def search_buses(self):
        params = [
            self.bus_id_search.text().strip() or None,
            self.route_search.text().strip() or None,
            self.bus_no_search.text().strip() or None,
            self.license_search.text().strip() or None,
            self.expiry_search.text().strip() or None,
            self.capacity_search.text().strip() or None,
            self.driver_search.text().strip() or None,
        ]
        rows = bus_ops.search_bus(params)
        self.bus_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            self.bus_table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.bus_table.setItem(i, 1, QTableWidgetItem(row["route"]))
            self.bus_table.setItem(i, 2, QTableWidgetItem(str(row["bus_no"])))
            self.bus_table.setItem(i, 3, QTableWidgetItem(row["license_no"]))
            self.bus_table.setItem(i, 4, QTableWidgetItem(str(row["expiry"])))
            self.bus_table.setItem(i, 5, QTableWidgetItem(str(row["capacity"])))
            self.bus_table.setItem(i, 6, QTableWidgetItem(str(row["driver_id"])))

    def select_bus(self, row, col):
        self.selected_bus_id = self.bus_table.item(row, 0).text()

    def clear_bus_selection(self):
        if not self.bus_table.selectedItems(): self.selected_bus_id = None

    def add_bus(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Bus")
        dialog.setMinimumWidth(600)

        layout = QVBoxLayout(dialog)

        # --- Form fields ---
        form_layout = QFormLayout()
        route_input = QLineEdit()
        bus_no_input = QSpinBox()
        bus_no_input.setRange(1, 9999)
        license_input = QLineEdit()
        expiry_input = create_calendar_field()
        capacity_input = QSpinBox()
        capacity_input.setRange(1, 149)
        driver_id_input = QSpinBox()
        driver_id_input.setRange(1, 9999)

        form_layout.addRow("Route:", route_input)
        form_layout.addRow("Bus No:", bus_no_input)
        form_layout.addRow("License No:", license_input)
        form_layout.addRow("Expiry:", expiry_input)
        form_layout.addRow("Capacity:", capacity_input)
        form_layout.addRow("Driver ID:", driver_id_input)

        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        clear_btn = QPushButton("Clear Form")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # --- Button actions ---
        def add_action():
            para = (
                route_input.text().strip(),
                bus_no_input.text().strip(),
                license_input.text().strip(),
                expiry_input.date().toString("yyyy-MM-dd"),
                capacity_input.text().strip(),
                driver_id_input.text().strip(),
            )

            if any(not field for field in para):
                QMessageBox.warning(dialog, "Missing Data", "Please fill all fields.")
                return

            try:
                bus_ops.insert_bus(para)
                QMessageBox.information(dialog, "Success", "Bus added successfully.")
                dialog.accept()
                self.search_buses()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", str(e))

        def clear_action():
            route_input.clear()
            bus_no_input.clear()
            license_input.clear()
            expiry_input.setDate(QDate.currentDate())
            capacity_input.clear()
            driver_id_input.clear()

        add_btn.clicked.connect(add_action)
        clear_btn.clicked.connect(clear_action)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()

    def update_bus(self):
        row = self.bus_table.currentRow()
        if not self.selected_bus_id or row < 0:
            QMessageBox.warning(self, "Update Bus", "No bus selected.")
            return

        bus_id     = int(self.bus_table.item(row, 0).text())
        route      = self.bus_table.item(row, 1).text()
        bus_no     = int(self.bus_table.item(row, 2).text())
        license_no = self.bus_table.item(row, 3).text()
        expiry     = self.bus_table.item(row, 4).text()
        capacity   = int(self.bus_table.item(row, 5).text())
        driver_id  = int(self.bus_table.item(row, 6).text())

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Update Bus ID: {self.selected_bus_id}")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # --- Form Fields ---
        id_label = QLabel(str(self.selected_bus_id))
        route_input = QLineEdit()
        route_input.setText(route)
        bus_no_input = QSpinBox(); bus_no_input.setRange(0, 9999)
        bus_no_input.setValue(bus_no)
        license_input = QLineEdit()
        license_input.setText(license_no)
        expiry_input = create_calendar_field(-5,10)
        expiry_input.setDate(QDate.fromString(expiry, "yyyy-MM-dd"))
        capacity_input = QSpinBox(); capacity_input.setRange(0, 149)
        capacity_input.setValue(capacity)
        driver_id_input = QSpinBox(); driver_id_input.setRange(0, 9999)
        driver_id_input.setValue(driver_id)

        form_layout.addRow("Bus ID:", id_label)
        form_layout.addRow("Route:", route_input)
        form_layout.addRow("Bus No:", bus_no_input)
        form_layout.addRow("License No:", license_input)
        form_layout.addRow("Expiry:", expiry_input)
        form_layout.addRow("Capacity:", capacity_input)
        form_layout.addRow("Driver ID:", driver_id_input)
        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        update_btn = QPushButton("Update")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(update_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # --- Button action ---
        def update_action():
            bus_no_val = bus_no_input.value()
            bus_no_val = None if bus_no_val == 0 else bus_no_val

            capacity_val = capacity_input.value()
            capacity_val = None if capacity_val == 0 else capacity_val

            driver_id_val = driver_id_input.value()
            driver_id_val = None if driver_id_val == 0 else driver_id_val

            expiry_qdate = expiry_input.date()
            expiry_val = None
            if expiry_qdate.isValid():
                expiry_val = expiry_qdate.toString("yyyy-MM-dd")

            params = (
                route_input.text().strip() or None,
                bus_no_val,
                license_input.text().strip() or None,
                expiry_val,
                capacity_val,
                driver_id_val,
                self.selected_bus_id,
            )

            try:
                bus_ops.update_bus(params)
                QMessageBox.information(dialog, "Success", "Bus updated successfully.")
                dialog.accept()
                self.search_buses()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", str(e))


        update_btn.clicked.connect(update_action)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()

    def delete_bus(self):
        if not self.selected_bus_id:
            QMessageBox.warning(self, "Delete Bus", "No bus selected.")
            return

        confirm = QMessageBox.question(self,"Confirm Delete",f"Delete Bus ID: {self.selected_bus_id}?",QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                bus_ops.delete_bus(self.selected_bus_id)
                QMessageBox.information(self, "Bus Deleted", f"Bus ID {self.selected_bus_id} deleted successfully.")
                self.selected_bus_id = None
                self.search_buses()
            except Exception as e:
                QMessageBox.warning(self, "Delete Failed", f"Could not delete Bus ID {self.selected_bus_id}.\n\nError: {str(e)}")


    # --- DRIVER FUNCTIONS ---
    def search_drivers(self):
        params = [
            self.driver_id_search.text().strip() or None,
            self.driver_name_search.text().strip() or None,
        ]
        rows = driver_ops.search(params)
        self.driver_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.driver_table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.driver_table.setItem(i, 1, QTableWidgetItem(row["name"]))

    def select_driver(self, row, col):
        self.selected_driver_id = self.driver_table.item(row, 0).text()

    def clear_driver_selection(self):
        if not self.driver_table.selectedItems():
            self.selected_driver_id = None

    def add_driver(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Driver")

        layout = QVBoxLayout(dialog)

        # --- Form fields ---
        form_layout = QFormLayout()
        name_input = QLineEdit()
        form_layout.addRow("Driver Name:", name_input)
        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        clear_btn = QPushButton("Clear Form")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # --- Button actions ---
        def add_action():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Missing Data", "Please fill all fields.")
                return

            try:
                driver_ops.insert_driver((name,))
                QMessageBox.information(dialog, "Success", "Driver added successfully.")
                dialog.accept()
                self.search_drivers()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", str(e))

        def clear_action():
            name_input.clear()

        def cancel_action():
            dialog.reject()

        add_btn.clicked.connect(add_action)
        clear_btn.clicked.connect(clear_action)
        cancel_btn.clicked.connect(cancel_action)

        dialog.exec()

    def update_driver(self):
        row = self.driver_table.currentRow()
        if not self.selected_driver_id or row < 0:
            QMessageBox.warning(self, "Update Driver", "No driver selected.")
            return

        driver_id = int(self.driver_table.item(row, 0).text())
        current_name = self.driver_table.item(row, 1).text()

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Update Driver ID: {driver_id}")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # --- Form Fields ---
        id_label = QLabel(str(driver_id))
        name_input = QLineEdit()
        name_input.setText(current_name)

        form_layout.addRow("Driver ID:", id_label)
        form_layout.addRow("Name:", name_input)
        layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        update_btn = QPushButton("Update")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(update_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # --- Button action ---
        def update_action():
            name_val = name_input.text().strip() or None
            params = (name_val, driver_id)

            try:
                driver_ops.update_driver(params)
                QMessageBox.information(dialog, "Success", "Driver updated successfully.")
                dialog.accept()
                self.search_drivers()
            except Exception as e:
                QMessageBox.warning(dialog, "Error", str(e))

        update_btn.clicked.connect(update_action)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()


    def delete_driver(self):
        if not self.selected_driver_id:
            QMessageBox.warning(self, "Delete Driver", "No driver selected.")
            return

        try:
            confirm = QMessageBox.question(self,"Confirm Delete",f"Delete Driver ID: {self.selected_driver_id}?",QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                driver_ops.delete_driver(self.selected_driver_id)
                QMessageBox.information(self, "Driver Deleted", "Driver deleted successfully.")
                self.selected_driver_id = None
                self.search_drivers()

        except Exception as e:
            print("Delete driver error:", repr(e))
            QMessageBox.warning(self, "Cannot Delete Driver", str(e))



    # --- PREDICTION FUNCTIONS ---
    def run_prediction_ui(self):
        bus_id = self.bus_id_input.text().strip()
        if not bus_id:
            QMessageBox.warning(self, "Missing Bus ID", "Please enter a Bus ID before predicting.")
            return

        self.pred_btn.setEnabled(False)
        self.pred_btn.setText("Predicting… Please wait")

        self._pred_thread = QThread()
        self._pred_worker = PredictionWorker(bus_id)

        self._pred_worker.moveToThread(self._pred_thread)

        self._pred_thread.started.connect(self._pred_worker.run)
        self._pred_worker.finished.connect(self.on_prediction_done)
        self._pred_worker.error.connect(self.on_prediction_error)
        self._pred_worker.finished.connect(self._pred_thread.quit)
        self._pred_worker.finished.connect(self._pred_worker.deleteLater)
        self._pred_thread.finished.connect(self._pred_thread.deleteLater)

        self._pred_thread.start()

    def on_prediction_done(self, preds, fig):
        self.pred_btn.setEnabled(True)
        self.pred_btn.setText("Predict")
        print("✅ Prediction complete:")
        plt.show(block=False)
        self.bus_id_input.clear()

    def on_prediction_error(self, msg):
        self.pred_btn.setEnabled(True)
        self.pred_btn.setText("Predict")
        QMessageBox.critical(self, "Prediction Error", msg)
        self.bus_id_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
