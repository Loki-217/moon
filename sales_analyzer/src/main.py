import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QComboBox
)
from analysis import analyze_data
from plotting import create_top_sales_chart, create_department_sales_chart

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('商超销售分析工具')
        self.layout = QVBoxLayout(self)
        self.df = None

        self.btn_open = QPushButton('打开销售报表')
        self.btn_open.clicked.connect(self.open_file)
        self.layout.addWidget(self.btn_open)

        self.combo_department = QComboBox()
        self.combo_department.addItems(["所有部门"])
        self.combo_department.currentTextChanged.connect(self.on_department_change)
        self.layout.addWidget(self.combo_department)

        self.label = QLabel('请先打开一个销售报表文件 (CSV 或 Excel格式)。')
        self.layout.addWidget(self.label)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.table_full_data = QTableWidget()
        self.table_restock = QTableWidget()
        self.table_slow_moving = QTableWidget()

        self.tabs.addTab(self.table_full_data, "完整报表")
        self.tabs.addTab(self.table_restock, "缺货提醒")
        self.tabs.addTab(self.table_slow_moving, "滞销商品")

        # Setup chart tab
        self.chart_tab = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_tab)
        self.canvas_top_sales = FigureCanvas(Figure(figsize=(10, 6)))
        self.canvas_dept_sales = FigureCanvas(Figure(figsize=(10, 6)))
        self.chart_layout.addWidget(self.canvas_top_sales)
        self.chart_layout.addWidget(self.canvas_dept_sales)
        self.tabs.addTab(self.chart_tab, "图表分析")

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "打开销售报表",
            "",
            "所有文件 (*);;CSV 文件 (*.csv);;Excel 文件 (*.xlsx)"
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
                self.label.setText("不支持的文件格式。")
                return

            self.df = df
            self.update_department_dropdown()
            self.run_analysis() # Initial analysis run
            self.label.setText(f"已成功加载并分析文件: {filepath}")
        except Exception as e:
            self.label.setText(f"加载文件时出错: {e}")

    def update_department_dropdown(self):
        if self.df is not None and '部门名称' in self.df.columns:
            departments = ["所有部门"] + self.df['部门名称'].unique().tolist()
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
        if department == "所有部门":
            df_to_analyze = self.df
        else:
            df_to_analyze = self.df[self.df['部门名称'] == department]

        self.display_data(self.table_full_data, df_to_analyze)
        restock_df, slow_moving_df = analyze_data(df_to_analyze)
        self.display_data(self.table_restock, restock_df)
        self.display_data(self.table_slow_moving, slow_moving_df)

        self.update_charts(df_to_analyze)

    def update_charts(self, df):
        department = self.combo_department.currentText()

        # Update top sales chart
        self.canvas_top_sales.figure.clear()
        top_sales_fig = create_top_sales_chart(df)
        self.canvas_top_sales.figure = top_sales_fig
        self.canvas_top_sales.draw()

        # Update department sales chart visibility
        if department == "所有部门":
            self.canvas_dept_sales.figure.clear()
            dept_sales_fig = create_department_sales_chart(self.df)
            self.canvas_dept_sales.figure = dept_sales_fig
            self.canvas_dept_sales.draw()
            self.canvas_dept_sales.setVisible(True)
        else:
            self.canvas_dept_sales.setVisible(False)

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
