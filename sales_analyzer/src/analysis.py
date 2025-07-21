import pandas as pd

def analyze_data(df):
    """
    Analyzes the sales data to identify products that need restocking and those that are slow-moving.

    Args:
        df (pd.DataFrame): The sales data.

    Returns:
        tuple: A tuple containing two DataFrames:
               - restock_df: Products that need restocking.
               - slow_moving_df: Slow-moving products.
    """
    # Assuming the columns are named 'product_name', 'barcode', 'stock', 'sales'
    # These names might need to be adjusted based on the actual file format.

    # Restock analysis
    restock_threshold = 10
    restock_df = df[df['stock'] < restock_threshold]

    # Slow-moving analysis
    slow_moving_threshold = 0
    slow_moving_df = df[df['sales'] <= slow_moving_threshold]

    return restock_df, slow_moving_df
