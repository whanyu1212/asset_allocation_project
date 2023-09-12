import pandas as pd
import numpy as np


def generate_asset_class_df(cfg, efficient_set, wealth=1000000):
    row = pd.DataFrame(
        efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][cfg["risky_assets"]]
    ).T

    store_df = pd.DataFrame()

    for i in cfg["weight"].keys():
        optimal_weight = cfg["weight"][i]
        store_df = pd.concat([store_df, row * optimal_weight * wealth])
    store_df = store_df.applymap("${:,.2f}".format)
    store_df.index = cfg["weight"].keys()
    return store_df


def calculate_agg_portfolio_return(subset_data, efficient_set, cfg):
    risky_assets_weights = efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][
        cfg["risky_assets"]
    ].values  # np array

    # Calculate the risk-free rate
    risk_free_rate = subset_data[cfg["risk_free_asset"]].mean() * 12

    risky_assets_returns = (
        subset_data.drop(["Date", "Period", cfg["risk_free_asset"]], axis=1).mean() * 12
        - risk_free_rate
    ).values

    store_list = []
    for i in cfg["weight"].keys():
        risky_weight = cfg["weight"][i]
        risk_free_weight = 1 - risky_weight

        portfolio_return = (risk_free_weight * risk_free_rate) + (
            np.dot(risky_assets_weights, risky_assets_returns)
        ) * risky_weight

        store_list.append(portfolio_return)

    portfolio_return_df = pd.DataFrame(
        store_list,
        index=cfg["weight"].keys(),
        columns=["Portfolio Return normalized by proportion of capital allocated"],
    )

    return portfolio_return_df.applymap("{:,.2f} %".format)


def calculate_agg_portfolio_risk(yearly_df, efficient_set, cfg):
    weights = efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][
        cfg["risky_assets"]
    ].values
    lst = []
    for i in cfg["weight"].keys():
        risky_allocation = cfg["weight"][i]
        cov_matrix = yearly_df.drop("Year", axis=1).cov()
        portfolio_variance = portfolio_variance = np.dot(
            weights.T, np.dot(cov_matrix, weights)
        )
        portfolio_risk = np.sqrt(portfolio_variance)
        porfolio_risk_normalized = risky_allocation * portfolio_risk
        lst.append(porfolio_risk_normalized)
    final_df = pd.DataFrame(
        lst,
        index=cfg["weight"].keys(),
        columns=["Portfolio Risk normalized by proportion of capital allocated"],
    )
    return final_df


def generate_group_asset_class_df(
    cfg, risk_value, subset_data, efficient_set, wealth=1000000
):
    row = pd.DataFrame(
        efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][cfg["risky_assets"]]
    ).T
    tbill_return = subset_data[cfg["risk_free_asset"]].mean() * 12
    store_df = pd.DataFrame()

    store_df = pd.concat([store_df, row * risk_value * wealth])

    store_df[cfg["risk_free_asset"]] = tbill_return * (1 - risk_value) * wealth
    store_df = store_df.applymap("${:,.2f}".format).reset_index(drop=True)
    return store_df
