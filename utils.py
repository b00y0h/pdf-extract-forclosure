# utils.py
def format_currency(value):
    """Format currency values with commas and dollar signs"""
    if isinstance(value, (int, float)):
        return f"${value:,.2f}"
    return value
