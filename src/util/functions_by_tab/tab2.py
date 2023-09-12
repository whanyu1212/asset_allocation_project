import plotly.express as px
import streamlit as st

import pandas as pd

from util.basic_utility import (
    highlight_max_by_column,
    highlight_min_by_column,
    parse_config,
)

# from util.basic_utility import highlight_max_by_column


def plot_corr_heatmap(yearly_df):
    yearly_corr = yearly_df.drop("Year", axis=1).corr()
    headers = yearly_df.drop("Year", axis=1).columns
    fig = px.imshow(
        yearly_corr,
        x=headers,
        y=headers,
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        text_auto=True,
        labels=dict(color="Correlation"),
    )

    fig.update_layout(title="Heatmap of Correlation Matrix:")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig)


def plot_cov_heatmap(yearly_df):
    yearly_cov = yearly_df.drop("Year", axis=1).cov()
    headers = yearly_df.drop("Year", axis=1).columns
    fig = px.imshow(
        yearly_cov,
        x=headers,
        y=headers,
        color_continuous_scale="Viridis",
        text_auto=True,
        labels=dict(color="Covariance"),
    )

    fig.update_layout(title="Heatmap of Covariance Matrix:")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig)


def generate_monthly_n_annual_stats_df(subset_data):
    monthly_annual_stats = (
        pd.melt(
            subset_data.drop("Period", axis=1),
            id_vars=["Date"],
            var_name="Indexes",
            value_name="Value",
        )
        .sort_values(by=["Date", "Indexes"])
        .groupby("Indexes")
        .agg(
            Monthly_average_return=("Value", "mean"),
            Monthly_sd=("Value", "std"),
        )
        .reset_index()
        .assign(Annualized_return=lambda x: x["Monthly_average_return"] * 12)
        .assign(Annualized_sd=lambda x: x["Monthly_sd"] * 12**0.5)
    )

    st.dataframe(
        monthly_annual_stats.style.apply(highlight_max_by_column),
        use_container_width=True,
        hide_index=True,
    )


def generate_monthly_n_annual_stats_df_approach2(subset_data, yearly_df):
    final = (
        pd.melt(
            subset_data.drop("Period", axis=1),
            id_vars=["Date"],
            var_name="Indexes",
            value_name="Value",
        )
        .sort_values(by=["Date", "Indexes"])
        .groupby("Indexes")
        .agg(
            Monthly_average_return=("Value", "mean"),
            Monthly_sd=("Value", "std"),
        )
        .reset_index()
    ).merge(
        (
            pd.melt(
                yearly_df,
                id_vars=["Year"],
                var_name="Indexes",
                value_name="Value",
            )
            .sort_values(by=["Year", "Indexes"])
            .groupby("Indexes")
            .agg(
                Annualized_return=("Value", "mean"),
                Annualized_sd=("Value", "std"),
            )
            .reset_index()
        ),
        on="Indexes",
    )
    st.dataframe(
        final.style.apply(highlight_max_by_column),
        use_container_width=True,
        hide_index=True,
    )


def generate_yearly_df_stats(subset_data):
    yearly_df = (
        subset_data.drop(["Period", "U.S. 30 Day TBill TR"], axis=1)
        .assign(
            Year=lambda x: x["Date"].apply(lambda x: x.split("-")[0]),
        )
        .drop("Date", axis=1)
        .groupby("Year")
        .sum()
        .reset_index()
    )
    return yearly_df
    # return yearly_df, yearly_df.cov(), yearly_df.corr(), yearly_df.columns
