import pandas as pd

def generate_order_suggestions(df):
    """
    Generates order suggestions based on sales data using accurate column names.
    Adds '建议订货数量' and '状态' columns.

    Args:
        df (pd.DataFrame): The sales data for a specific supplier.

    Returns:
        pd.DataFrame: The dataframe with added suggestion columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Make a copy to avoid SettingWithCopyWarning
    suggested_df = df.copy()

    # --- Use accurate column names based on user feedback ---
    sales_col = '销售数量'
    stock_col = '现存数量'
    suggestion_col = '建议订货数量'
    status_col = '状态'

    # Calculate '建议订货数量'
    if sales_col in suggested_df.columns:
        # Ensure sales data is numeric, coercing errors to 0
        suggested_df[suggestion_col] = pd.to_numeric(suggested_df[sales_col], errors='coerce').fillna(0)
    else:
        suggested_df[suggestion_col] = 0

    # Determine '状态'
    if stock_col in suggested_df.columns and sales_col in suggested_df.columns:
        # Ensure stock data is numeric
        stock_numeric = pd.to_numeric(suggested_df[stock_col], errors='coerce').fillna(0)
        sales_numeric = pd.to_numeric(suggested_df[sales_col], errors='coerce').fillna(0)

        suggested_df[status_col] = '建议补货'
        suggested_df.loc[stock_numeric >= sales_numeric, status_col] = ''
    else:
        suggested_df[status_col] = ''

    return suggested_df

def get_restock_summary(df):
    """
    Filters the dataframe to get only the rows that need restocking.

    Args:
        df (pd.DataFrame): The dataframe with suggestion columns.

    Returns:
        pd.DataFrame: A filtered dataframe containing only items that need restocking.
    """
    if df is None or df.empty or '状态' not in df.columns:
        return pd.DataFrame()

    return df[df['状态'] == '建议补货']
