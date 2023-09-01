import yaml
import pandas as pd
import numpy as np


def highlight_max(s):
    is_max = s == s.max()
    return ["background-color: LightCoral" if v else "" for v in is_max]


def parse_config(path):
    with open(path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


latex_formula = r"""\begin{align*}
            &\text{Monthly Average Return} : \frac{1}{n} \sum_{i=1}^{n} X_i & \text{Monthly Standard Deviation} : \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2} \\
            &\text{Annual Average Return} : 12 \times \bar{X} & \text{Annual Standard Deviation} : \sqrt{12} \times \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(X_i - \bar{X})^2}
            \end{align*}
            """
portfolio_return_latex = (
    r"""\text{Porfolio Return} :\R_p = R_f + \sum_{i=1}^{n} w_i \cdot (R_i - R_f)"""
)
portfolio_risk_latex = r"""
            \text{Porfolio Risk} :\sigma_p = \sqrt{\sum \left[ w_i \cdot \sigma_i \right]^2 + \sum\sum \left[ w_i \cdot w_j \cdot \sigma_i \cdot \sigma_j \cdot \rho_{ij} \right]}"""


def generate_asset_class_df(cfg, efficient_set, wealth=1000000):
    row = pd.DataFrame(
        efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][
            ["Russell 2000 TR ", "S&P 500 TR ", "LB LT Gvt/Credit TR ", "MSCI EAFE TR "]
        ]
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
        ["Russell 2000 TR ", "S&P 500 TR ", "LB LT Gvt/Credit TR ", "MSCI EAFE TR "]
    ].values  # np array

    # Calculate the risk-free rate
    risk_free_rate = subset_data["U.S. 30 Day TBill TR "].mean() * 12

    risky_assets_returns = (
        subset_data.drop(["Date", "Period", "U.S. 30 Day TBill TR "], axis=1).mean()
        * 12
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
        ["Russell 2000 TR ", "S&P 500 TR ", "LB LT Gvt/Credit TR ", "MSCI EAFE TR "]
    ].values
    lst = []
    for i in cfg["weight"].keys():
        risky_allocation = cfg["weight"][i]
        cov_matrix = yearly_df.cov()
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
    risk_value, subset_data, efficient_set, wealth=1000000
):
    row = pd.DataFrame(
        efficient_set.loc[efficient_set.Sharpe_Ratio.idxmax()][
            ["Russell 2000 TR ", "S&P 500 TR ", "LB LT Gvt/Credit TR ", "MSCI EAFE TR "]
        ]
    ).T
    tbill_return = subset_data["U.S. 30 Day TBill TR "].mean() * 12
    store_df = pd.DataFrame()

    store_df = pd.concat([store_df, row * risk_value * wealth])

    store_df["U.S. 30 Day TBill TR "] = tbill_return * (1 - risk_value) * wealth
    store_df = store_df.applymap("${:,.2f}".format).reset_index(drop=True)
    return store_df
