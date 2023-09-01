import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import linregress


def minimize_std(expected_returns, cov_matrix, target_mean_returns):
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

        # Define bounds for the weights (0 to 1, meaning fully invested or not invested)
        # bounds = [(0, 1) for _ in expected_returns]
        bounds = [(0, None) for _ in range(len(expected_returns))]

        # Define the optimization problem with both constraints
        constraints = [
            {"type": "eq", "fun": mean_return_constraint},
            {"type": "eq", "fun": budget_constraint},
        ]

        # Use the minimize function to solve the optimization problem
        optimal_weights = minimize(
            portfolio_std_deviation,  # Objective function to minimize
            initial_weights,
            cov_matrix,
            method="trust-constr",  # Sequential Least Squares Quadratic Programming
            constraints=constraints,  # Constraints
            bounds=bounds,  # Bounds for asset weights
        )

        # Extract the optimized portfolio weights
        optimized_weights = optimal_weights.x

        # Calculate the minimum standard deviation for the current target
        min_std_dev = portfolio_std_deviation(optimized_weights, cov_matrix)

        # Print the results for the current target
        row = (
            [min_std_dev]
            + optimized_weights.tolist()
            + [np.dot(expected_returns, optimized_weights)]
        )
        rows.append(row)
    output = pd.DataFrame(
        rows,
        columns=["min_std_dev"]
        + expected_returns.index.tolist()
        + ["portfolio_mean_return"],
    )
    final = pd.concat(
        [pd.DataFrame(target_mean_returns, columns=["target_mean_returns"]), output],
        axis=1,
    ).assign(Sharpe_Ratio=lambda x: x["portfolio_mean_return"] / x["min_std_dev"])

    return final


def find_tangent_line(efficient_set, subset_data):
    x = [0]
    y = [subset_data["U.S. 30 Day TBill TR "].mean() * 12]
    x.append(efficient_set.loc[efficient_set["Sharpe_Ratio"].idxmax(), "min_std_dev"])
    y.append(
        efficient_set.loc[
            efficient_set["Sharpe_Ratio"].idxmax(), "portfolio_mean_return"
        ]
    )
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    new_x = np.array([40, 45, 50, 55, 60])

    # Use the linear equation to predict y-values
    new_y = slope * new_x + intercept

    x.extend(new_x)
    y.extend(new_y)

    df = pd.DataFrame({"tangent_x": x, "tangent_y": y})
    return df
