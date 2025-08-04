import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QListWidget,
    QHBoxLayout, QScrollArea
)
from analysis import generate_order_suggestions, get_restock_summary
from plotting import create_top_sales_chart, create_department_sales_chart

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtGui import QColor
from matplotlib.figure import Figure

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('智能采购订单助手')
        self.setGeometry(100, 100, 1200, 800) # Set a larger default window size
        self.df = None

        # Main layout
        main_layout = QHBoxLayout(self)

        # Left panel for supplier list
        left_panel = QVBoxLayout()
        self.supplier_list = QListWidget()
        left_panel.addWidget(QLabel("供应商列表"))
        left_panel.addWidget(self.supplier_list)

        # Right panel for tabs
        right_panel = QVBoxLayout()
        self.tabs = QTabWidget()
        right_panel.addWidget(self.tabs)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 1) # 1 part width
        main_layout.addLayout(right_panel, 4) # 4 parts width

        # Create tabs and their layouts
        self.order_detail_tab = QWidget()
        self.order_detail_layout = QVBoxLayout(self.order_detail_tab)
        self.order_detail_table = QTableWidget()
        self.order_detail_layout.addWidget(self.order_detail_table)

        self.restock_summary_tab = QWidget()
        self.restock_summary_layout = QVBoxLayout(self.restock_summary_tab)
        self.restock_summary_table = QTableWidget()
        self.restock_summary_layout.addWidget(self.restock_summary_table)

        # Chart tab setup with scroll area
        self.chart_tab = QScrollArea()
        self.chart_tab.setWidgetResizable(True)
        chart_container = QWidget()
        self.chart_layout = QVBoxLayout(chart_container)
        self.canvas_top_sales = FigureCanvas(Figure(figsize=(10, 8)))
        self.canvas_dept_sales = FigureCanvas(Figure(figsize=(10, 8)))
        self.chart_layout.addWidget(self.canvas_top_sales)
        self.chart_layout.addWidget(self.canvas_dept_sales)
        self.chart_tab.setWidget(chart_container)

        self.tabs.addTab(self.order_detail_tab, "订单详情")
        self.tabs.addTab(self.restock_summary_tab, "缺货商品汇总")
        self.tabs.addTab(self.chart_tab, "图表分析")

        # Add buttons to the left panel
        self.btn_open = QPushButton('打开总销售报表')
        self.btn_open.clicked.connect(self.open_file)
        self.btn_export = QPushButton('导出当前订单')
        self.btn_export.clicked.connect(self.export_order)
        left_panel.addWidget(self.btn_open)
        left_panel.addWidget(self.btn_export)

        # Connect supplier list signal
        self.supplier_list.currentItemChanged.connect(self.on_supplier_change)

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
            # Step 1: Find the header row by inspecting the first few rows
            header_row_index = self.find_header_row(filepath)
            if header_row_index is None:
                print("Error: Could not find the header row. Please check the file format.")
                # Optionally, show a message box to the user
                return

            # Step 2: Load the full dataframe using the correct header index
            self.df = pd.read_excel(filepath, header=header_row_index)

            # Step 3: Validate required columns
            required_cols = ['最新货商名称', '销售数量', '现存数量', '商品编码', '商品名称']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            if missing_cols:
                print(f"Error: The following required columns are missing: {', '.join(missing_cols)}")
                self.df = None
                return

            self.update_supplier_list()
            if self.supplier_list.count() > 0:
                self.supplier_list.setCurrentRow(0)

        except Exception as e:
            print(f"An unexpected error occurred while loading the file: {e}")
            self.df = None

    def find_header_row(self, filepath, max_rows_to_scan=10):
        """
        Scans the first few rows of an Excel file to find the correct header row.
        The header row is identified by the presence of key column names.
        """
        try:
            # Read the first few rows without assuming a header
            df_preview = pd.read_excel(filepath, header=None, nrows=max_rows_to_scan)

            # Define keywords to identify the header row
            header_keywords = ['商品编码', '商品名称', '主条码', '部门名称']

            for index, row in df_preview.iterrows():
                row_values = set(str(v) for v in row.values)
                # Check if a significant number of keywords are in the row
                if len(set(header_keywords) & row_values) >= 2:
                    return index
        except Exception as e:
            print(f"Error while scanning for header row: {e}")

        return None

    def update_supplier_list(self):
        self.supplier_list.clear()
        if self.df is None or '最新货商名称' not in self.df.columns:
            return

        # Use '含税销售额' if available, otherwise calculate it.
        if '含税销售额' in self.df.columns:
            supplier_sales = self.df.groupby('最新货商名称')['含税销售额'].sum()
        elif '销售数量' in self.df.columns and '标准售价' in self.df.columns:
            df_copy = self.df.copy()
            df_copy[' calculated_sales'] = df_copy['销售数量'] * df_copy['标准售价']
            supplier_sales = df_copy.groupby('最新货商名称')[' calculated_sales'].sum()
        else:
            # If no sales data, sort by name
            suppliers = sorted(self.df['最新货商名称'].unique())
            self.supplier_list.addItems(suppliers)
            return

        # Sort suppliers by total sales in descending order
        sorted_suppliers = supplier_sales.sort_values(ascending=False).index.tolist()
        self.supplier_list.addItems(sorted_suppliers)


    def on_supplier_change(self, current, previous):
        if current is None:
            return

        supplier = current.text()

        if self.df is None:
            return

        if supplier == "所有供应商": # This case should no longer happen, but as a fallback
            df_to_analyze = self.df
        else:
            df_to_analyze = self.df[self.df['最新货商名称'] == supplier]

        self.update_order_details(df_to_analyze)

    def export_order(self):
        if self.order_detail_table.rowCount() == 0:
            print("No data to export.")
            # Optionally, show a message box to the user
            return

        current_supplier_item = self.supplier_list.currentItem()
        if not current_supplier_item:
            print("Please select a supplier to export.")
            return

        supplier_name = current_supplier_item.text()
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{supplier_name}-采购订单-{date_str}.xlsx"

        filepath, _ = QFileDialog.getSaveFileName(self, "保存订单", filename, "Excel Files (*.xlsx)")

        if not filepath:
            return

        # Re-generate the suggested dataframe for export to ensure it's clean
        df_to_export = self.df[self.df['最新货商名称'] == supplier_name]
        suggested_df = generate_order_suggestions(df_to_export)

        # Define the exact columns and their order for the export file
        export_columns = [
            '主条码', '商品名称', '部门名称', '单位', '销售数量',
            '现存数量', '标准售价', '建议订货数量', '实际订货数量'
        ]

        # Add '实际订货数量' column, leaving it empty
        suggested_df['实际订货数量'] = ''

        # Filter and reorder the dataframe to match the desired format
        final_df = suggested_df[[col for col in export_columns if col in suggested_df.columns]]

        try:
            final_df.to_excel(filepath, index=False)
            print(f"Order exported successfully to {filepath}")
        except Exception as e:
            print(f"Error exporting file: {e}")


    def update_order_details(self, df):
        if df is None:
            return

        # Generate suggestions
        suggested_df = generate_order_suggestions(df)

        # Update the order detail table
        self.display_data(self.order_detail_table, suggested_df)

        # Update the restock summary table
        restock_summary_df = get_restock_summary(suggested_df)
        self.display_data(self.restock_summary_table, restock_summary_df)

        # Update charts
        self.update_charts(suggested_df)

    def update_charts(self, df):
        # This function now needs to be adapted to the new UI logic
        # For now, let's just update the top sales chart for the selected supplier/all

        # Update top sales chart
        self.canvas_top_sales.figure.clear()
        top_sales_fig = create_top_sales_chart(df)
        self.canvas_top_sales.figure = top_sales_fig
        self.canvas_top_sales.draw()

        # The logic for the second chart (department sales) can be simplified.
        # It will always show the sales by department for the currently selected data (df).
        self.canvas_dept_sales.figure.clear()
        dept_sales_fig = create_department_sales_chart(df)
        self.canvas_dept_sales.figure = dept_sales_fig
        self.canvas_dept_sales.draw()

    def display_data(self, table, df):
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[i, j]))
                # Highlight rows that need restocking
                if '状态' in df.columns and df.iat[i, df.columns.get_loc('状态')] == '建议补货':
                    item.setBackground(QColor(255, 224, 224)) # Light red
                table.setItem(i, j, item)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
