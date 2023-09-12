import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from scipy.optimize import minimize
from scipy.stats import linregress


def trust_region_solver(expected_returns, cov_matrix, target_mean_returns):
    rows = []
    # Loop through each target mean return and optimize the portfolio
    for target_mean_return in target_mean_returns:
        # Define the constraint function for the current target mean return
        def portfolio_std_deviation(weights, cov_matrix):
            portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return portfolio_stddev

        # Define the constraint function for target mean return
        def mean_return_constraint(weights):
            return np.sum(expected_returns * weights) - target_mean_return

        # Define the constraint to ensure the weights add up to 1 (fully invested)
        def budget_constraint(weights):
            return np.sum(weights) - 1

        # Define the initial guess for portfolio weights
        initial_weights = np.ones(len(expected_returns)) / len(expected_returns)

        # bounds = [(0, None) for _ in range(len(expected_returns))]

        # Define the optimization problem with both constraints
        constraints = [
            {"type": "eq", "fun": mean_return_constraint},
            {"type": "eq", "fun": budget_constraint},
        ]

        # Use the minimize function to solve the optimization problem
        optimal_weights = minimize(
            portfolio_std_deviation,
            initial_weights,
            cov_matrix,
            method="trust-constr",
            constraints=constraints,
            # bounds=bounds,
        )

        # Extract the optimized portfolio weights
        optimized_weights = optimal_weights.x

        # Calculate the minimum standard deviation for the current target
        min_std_dev = portfolio_std_deviation(optimized_weights, cov_matrix)

        # Print the results for the current target as a list
        row = (
            [min_std_dev]
            + optimized_weights.tolist()
            + [np.dot(expected_returns, optimized_weights)]
        )
        rows.append(row)
    # Concatenate the rows together to form a dataframe
    output = pd.DataFrame(
        rows,
        columns=["min_std_dev"]
        + expected_returns.index.tolist()
        + ["portfolio_mean_return"],
    )
    # Calculate the Sharpe Ratio for each portfolio
    final = pd.concat(
        [pd.DataFrame(target_mean_returns, columns=["target_mean_returns"]), output],
        axis=1,
    ).assign(Sharpe_Ratio=lambda x: x["portfolio_mean_return"] / x["min_std_dev"])

    return final


def find_tangent_line(efficient_set, subset_data, cfg):
    x_coord = [0]
    y_coord = [subset_data[cfg["risk_free_asset"]].mean() * 12]  # y intercept
    x_coord.append(
        efficient_set.loc[efficient_set["Sharpe_Ratio"].idxmax(), "min_std_dev"]
    )
    y_coord.append(
        efficient_set.loc[
            efficient_set["Sharpe_Ratio"].idxmax(), "portfolio_mean_return"
        ]
    )
    # The _ represents r_value, p_value and std_err in the linregress function (sequentially)
    slope, intercept, _, _, _ = linregress(x_coord, y_coord)
    # Use a few random x-values to extend the tangent line from the optimal portfolio
    new_x = np.array([1.0, 5.0, 10.0, 15.0, 20.0])

    # Use the linear equation to predict y-values
    new_y = slope * new_x + intercept

    # Extend the x and y coordinate lists
    x_coord.extend(new_x)
    y_coord.extend(new_y)

    df = pd.DataFrame({"tangent_x": x_coord, "tangent_y": y_coord})
    return df


def generate_efficient_frontier_plot(efficient_set, x_scale, y_scale, tangent_df):
    chart = (
        alt.Chart(efficient_set)
        .mark_circle(size=60)
        .encode(
            x=alt.X(
                "min_std_dev",
                scale=x_scale,
                axis=alt.Axis(title="Anualized Volatility", tickCount=5),
            ),
            y=alt.Y(
                "target_mean_returns",
                scale=y_scale,
                axis=alt.Axis(title="Anualized Expected Return", tickCount=5),
            ),
            tooltip=efficient_set.columns.tolist(),
            color=alt.Color(
                "Sharpe_Ratio:Q",
                scale=alt.Scale(
                    range=["orange", "red", "blue"]
                ),  # easier to see with a different color scheme
            ),
        )
        .properties(
            width=600,
            height=500,
            title="Efficient Frontier Set & CML: ",
        )
        .interactive()
    )
    line_chart = (
        alt.Chart(tangent_df)
        .mark_line(color="red", strokeDash=[5, 5])
        .encode(
            x=alt.X(
                "tangent_x",
            ),
            y=alt.Y(
                "tangent_y",
            ),
        )
    )
    st.altair_chart(chart + line_chart, theme="streamlit", use_container_width=True)
