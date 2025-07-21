# Sales Analyzer

This is a simple desktop application for analyzing sales data from CSV or Excel files. It helps identify products that need restocking and those that are slow-moving.

## Features

- Open and read sales data from `.csv` and `.xlsx` files.
- Displays the full sales report.
- Analyzes and displays a list of products that need to be restocked (stock < 10).
- Analyzes and displays a list of slow-moving products (sales <= 0).

## How to Use

### Running the application

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application**:
    ```bash
    python src/main.py
    ```

### Creating an executable

1.  **Install PyInstaller**:
    ```bash
    pip install pyinstaller
    ```

2.  **Package the application**:
    ```bash
    pyinstaller --onefile --windowed --name SalesAnalyzer src/main.py
    ```
    This will create a single executable file in the `dist` directory.

## File Format

The application assumes your sales data has at least the following columns:
- `product_name`: The name of the product.
- `stock`: The current stock level.
- `sales`: The sales figure for a given period.

A sample file is provided at `data/sample_sales.csv`.
