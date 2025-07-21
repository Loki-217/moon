import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QComboBox
)
from analysis import analyze_data

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sales Analyzer')
        self.layout = QVBoxLayout(self)
        self.df = None

        self.btn_open = QPushButton('Open Sales Report')
        self.btn_open.clicked.connect(self.open_file)
        self.layout.addWidget(self.btn_open)

        self.combo_department = QComboBox()
        self.combo_department.addItems(["All Departments"])
        self.combo_department.currentTextChanged.connect(self.on_department_change)
        self.layout.addWidget(self.combo_department)

        self.label = QLabel('Please open a sales report file (CSV or Excel).')
        self.layout.addWidget(self.label)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.table_full_data = QTableWidget()
        self.table_restock = QTableWidget()
        self.table_slow_moving = QTableWidget()

        self.tabs.addTab(self.table_full_data, "Full Report")
        self.tabs.addTab(self.table_restock, "Restock Needed")
        self.tabs.addTab(self.table_slow_moving, "Slow-Moving")

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Sales Report",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if filepath:
            self.load_data(filepath)

    def load_data(self, filepath):
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                self.label.setText("Unsupported file format.")
                return

            self.df = df
            self.update_department_dropdown()
            self.run_analysis() # Initial analysis run
            self.label.setText(f"Loaded and analyzed {filepath}")
        except Exception as e:
            self.label.setText(f"Error loading file: {e}")

    def update_department_dropdown(self):
        if self.df is not None and '部门名称' in self.df.columns:
            departments = ["All Departments"] + self.df['部门名称'].unique().tolist()
            self.combo_department.blockSignals(True)
            self.combo_department.clear()
            self.combo_department.addItems(departments)
            self.combo_department.blockSignals(False)

    def on_department_change(self, text):
        self.run_analysis()

    def run_analysis(self):
        if self.df is None:
            return

        department = self.combo_department.currentText()
        if department == "All Departments":
            df_to_analyze = self.df
        else:
            df_to_analyze = self.df[self.df['部门名称'] == department]

        self.display_data(self.table_full_data, df_to_analyze)
        restock_df, slow_moving_df = analyze_data(df_to_analyze)
        self.display_data(self.table_restock, restock_df)
        self.display_data(self.table_slow_moving, slow_moving_df)

    def display_data(self, table, df):
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
