import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Set the default font to support Chinese characters
plt.rcParams['font.sans-serif'] = ['SimHei']  # Or any other Chinese font you have
plt.rcParams['axes.unicode_minus'] = False  # To display the minus sign correctly

def create_top_sales_chart(df, top_n=10):
    """
    Creates a bar chart for top N selling products.
    """
    if df is None or df.empty or '销售数量' not in df.columns or '商品名称' not in df.columns:
        return Figure() # Return an empty figure if data is invalid

    # Sort by sales and get top N
    top_df = df.nlargest(top_n, '销售数量')

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    bars = ax.bar(top_df['商品名称'], top_df['销售数量'])
    ax.set_title(f'销售量前{top_n}名商品')
    ax.set_ylabel('销售数量')
    ax.tick_params(axis='x', rotation=45)

    # Add data labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom') # va: vertical alignment

    fig.tight_layout()
    return fig

def create_department_sales_chart(df):
    """
    Creates a bar chart comparing sales across departments.
    """
    if df is None or df.empty or '销售数量' not in df.columns or '部门名称' not in df.columns:
        return Figure()

    # Group by department and sum sales
    dept_sales = df.groupby('部门名称')['销售数量'].sum().sort_values(ascending=False)

    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    bars = ax.bar(dept_sales.index, dept_sales.values)
    ax.set_title('各部门销售业绩对比')
    ax.set_ylabel('总销售数量')
    ax.tick_params(axis='x', rotation=45)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom')

    fig.tight_layout()
    return fig
