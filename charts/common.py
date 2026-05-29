"""
Shared chart utilities, theme configuration, and decorators.
"""

from functools import wraps
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from constants import Colors, CHART_COLORWAY


def configure_theme():
    """Configure the global Plotly theme for all charts."""
    pio.templates["ccrec_theme"] = dict(
        layout=dict(
            paper_bgcolor=Colors.WHITE,
            plot_bgcolor=Colors.PLOT_BG,
            font=dict(
                color=Colors.BLACK,
                family="Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif",
                size=12,
            ),
            colorway=CHART_COLORWAY,
            title=dict(
                font=dict(size=15, color=Colors.BLACK, family="Segoe UI, sans-serif"),
                x=0.02,
                xanchor='left',
            ),
            margin=dict(l=50, r=30, t=50, b=40),
            legend=dict(
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor=Colors.PALE_GREY,
                borderwidth=1,
                font=dict(size=11),
            ),
            xaxis=dict(
                gridcolor="#E8E9EA",
                linecolor=Colors.PALE_GREY,
                zerolinecolor=Colors.PALE_GREY,
            ),
            yaxis=dict(
                gridcolor="#E8E9EA",
                linecolor=Colors.PALE_GREY,
                zerolinecolor=Colors.PALE_GREY,
            ),
        )
    )
    pio.templates.default = "ccrec_theme"


def get_empty_figure(message: str = "No data available") -> go.Figure:
    """
    Create a styled empty figure with a centered message.

    Parameters
    ----------
    message : str
        Message to display in the center of the figure.

    Returns
    -------
    go.Figure
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color=Colors.CHARCOAL),
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def safe_chart(default_title: str = "No Data Available"):
    """
    Decorator that returns an empty figure if the chart function fails
    or receives an empty DataFrame.

    Parameters
    ----------
    default_title : str
        Message shown when chart cannot be generated.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if args and isinstance(args[0], pd.DataFrame) and len(args[0]) == 0:
                    return get_empty_figure(default_title)
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Chart error in {func.__name__}: {e}")
                return get_empty_figure(f"{default_title} (Error)")
        return wrapper
    return decorator


def sort_by_grade(df: pd.DataFrame, grade_col: str = 'Grade Level') -> pd.DataFrame:
    """Sort a DataFrame by grade level numerically."""
    grades = df[grade_col].drop_duplicates().tolist()
    grade_order = {g: int(g) for g in grades if g.isdigit()}
    df = df.copy()
    df.sort_values(
        grade_col,
        key=lambda x: x.map(grade_order),
        inplace=True
    )
    return df


# Initialize theme on import
configure_theme()