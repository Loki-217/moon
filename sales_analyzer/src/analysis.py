import pandas as pd

def generate_order_suggestions(df):
    """
    Generates order suggestions based on sales data.
    Adds '建议订货量' and '状态' columns.

    Args:
        df (pd.DataFrame): The sales data for a specific supplier.

    Returns:
        pd.DataFrame: The dataframe with added suggestion columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Make a copy to avoid SettingWithCopyWarning
    suggested_df = df.copy()

    # Calculate '建议订货量'
    if '销售数量' in suggested_df.columns:
        suggested_df['建议订货量'] = suggested_df['销售数量']
    else:
        suggested_df['建议订货量'] = 0 # Default to 0 if no sales data

    # Determine '状态'
    if '现存数量' in suggested_df.columns and '销售数量' in suggested_df.columns:
        suggested_df['状态'] = suggested_df.apply(
            lambda row: '建议补货' if row['现存数量'] < row['销售数量'] else '',
            axis=1
        )
    else:
        suggested_df['状态'] = ''

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
