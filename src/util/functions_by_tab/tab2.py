import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import gmean
from util.basic_utility import (
    highlight_max_by_column,
    highlight_min_by_column,
    parse_config,
)


def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod() ** (1.0 / len(a))


def generate_monthly_n_annual_stats_df(subset_data, yearly_df):
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
            Monthly_return=("Value", "mean"),
            Monthly_std=("Value", "std"),
        )
        .reset_index()
        .assign(Annual_arithmetic_return=lambda x: x["Monthly_return"] * 12)
        .assign(Annualized_std=lambda x: x["Monthly_std"] * 12**0.5)
    )

    geom_mean_lst = []
    annual_std = []
    for col in monthly_annual_stats["Indexes"]:
        iterable = [i + 1 for i in (yearly_df.drop("Year", axis=1) / 100)[col].tolist()]
        geom_mean_lst.append((geo_mean(iterable) - 1) * 100)
        annual_std.append(yearly_df.drop("Year", axis=1)[col].std())
    monthly_annual_stats["Annualized_std(2)"] = annual_std
    monthly_annual_stats["Annual_geometric_return"] = geom_mean_lst
    monthly_annual_stats = monthly_annual_stats[
        [
            "Indexes",
            "Monthly_return",
            "Monthly_std",
            "Annual_arithmetic_return",
            "Annual_geometric_return",
            "Annualized_std",
            "Annualized_std(2)",
        ]
    ]

    st.dataframe(
        monthly_annual_stats.style.apply(highlight_max_by_column),
        use_container_width=True,
        hide_index=True,
    )


def plot_corr_heatmap_by_month(subset_data, cfg):
    corr_matrix = subset_data.drop(
        ["Date", "Period", cfg["risk_free_asset"]], axis=1
    ).corr()
    headers = subset_data.drop(
        ["Date", "Period", cfg["risk_free_asset"]], axis=1
    ).columns
    fig = px.imshow(
        corr_matrix,
        x=headers,
        y=headers,
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        text_auto=True,
        labels=dict(color="Correlation"),
    )

    fig.update_layout(title="Heatmap of Correlation Matrix (Month):")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig)


def plot_corr_heatmap_by_year(yearly_df, cfg):
    yearly_corr = yearly_df.drop(["Year", cfg["risk_free_asset"]], axis=1).corr()
    headers = yearly_df.drop(["Year", cfg["risk_free_asset"]], axis=1).columns
    fig = px.imshow(
        yearly_corr,
        x=headers,
        y=headers,
        color_continuous_scale="Burgyl",
        text_auto=True,
        labels=dict(color="Correlation"),
    )

    fig.update_layout(title="Heatmap of Correlation Matrix (Year):")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig)


def generate_yearly_df_stats(subset_data):
    yearly_df = (
        subset_data.drop(["Period"], axis=1)
        .assign(
            Year=lambda x: x["Date"].apply(lambda x: x.split("-")[0]),
        )
        .drop("Date", axis=1)
        .groupby("Year")
        .sum()
        .reset_index()
    )
    return yearly_df
