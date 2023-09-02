import plotly.express as px
import streamlit as st
import pandas as pd


def create_line_chart(subset_data_pivot: pd.DataFrame) -> None:
    fig = px.line(
        subset_data_pivot,
        x="Date",
        y="Value",
        color="Indexes",
        markers=True,
    )
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(count=3, label="3y", step="year", stepmode="backward"),
                        dict(count=5, label="5y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        xaxis_range=[min(subset_data_pivot.Date), max(subset_data_pivot.Date)],
    )
    st.plotly_chart(fig, use_container_width=True)
