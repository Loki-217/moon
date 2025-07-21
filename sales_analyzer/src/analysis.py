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
    # Using column names provided by the user.
    # '现存数量' for stock, '销售数量' for sales.

    # Restock analysis
    restock_threshold = 10
    # Ensure the column exists before trying to access it
    if '现存数量' in df.columns:
        restock_df = df[df['现存数量'] < restock_threshold]
    else:
        restock_df = pd.DataFrame() # Return empty dataframe if column not found

    # Slow-moving analysis
    slow_moving_threshold = 0
    if '销售数量' in df.columns:
        slow_moving_df = df[df['销售数量'] <= slow_moving_threshold]
    else:
        slow_moving_df = pd.DataFrame() # Return empty dataframe if column not found

    return restock_df, slow_moving_df
