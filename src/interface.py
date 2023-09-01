import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from util.utility import (
    highlight_max,
    parse_config,
    latex_formula,
    portfolio_return_latex,
    portfolio_risk_latex,
    generate_asset_class_df,
    calculate_agg_portfolio_return,
    calculate_agg_portfolio_risk,
    generate_group_asset_class_df,
)
from optimization.portfolio_std_solver import minimize_std, find_tangent_line

pd.options.display.precision = None
st.set_page_config(layout="wide")
st.title("Navigating Asset Allocation")


data = pd.read_csv("./data/processed/processed_data.csv")
cfg = parse_config("./cfg/config.yml")

# Sidebar configuration
with st.sidebar:
    header = st.header("Configurations")
    st.divider()
    time_range = st.radio(
        "Choose the period of time you want to analyze:",
        ["1980s", "1990s", "2000s"],
        captions=["High Inflation", "The equity market bull-run", "Financial Crisis"],
    )
    indexes_options = st.multiselect(
        "Zoom into the specific indexes on the time series plot:",
        cfg["indexes_options"],
        cfg["indexes_options"],
    )
    st.text("")
    risk_value = st.slider(
        "Select a weightage to assign to the risky assets", 0.0, 1.0, 0.5
    )
    st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        ":bar_chart: Exploratory Analysis",
        ":pencil2: Calculations",
        ":chart_with_upwards_trend: Efficient Frontier",
        ":money_with_wings: Optimal Capital Allocation",
        ":speech_balloon: Chat with your data",
    ]
)

with tab1:
    subset_data = data[data["Period"] == time_range]
    print([subset_data["U.S. 30 Day TBill TR "].mean() * 12])
    st.subheader(f"Summary Statistics: {time_range}")
    st.dataframe(subset_data.describe(), use_container_width=True)
    st.divider()
    st.subheader("Time Series Plot")
    subset_data_pivot = (
        pd.melt(
            subset_data.drop("Period", axis=1),
            id_vars=["Date"],
            var_name="Indexes",
            value_name="Value",
        )
        .sort_values(by=["Date", "Indexes"])
        .query("Indexes in @indexes_options")
    )
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
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.latex(latex_formula)
    st.divider()

    monthly_annual_stats = (
        pd.melt(
            data.query("Period==@time_range").drop("Period", axis=1),
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
    max_values = monthly_annual_stats.select_dtypes(include=["number"]).max()
    st.markdown("**Monthly and Annual Average Return and Standard Deviation**")
    st.dataframe(
        monthly_annual_stats.style.apply(highlight_max),
        use_container_width=True,
        width=200,
        hide_index=True,
    )
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        # df1 = data.query("Period==@time_range").drop(
        #     ["Date", "Period", "U.S. 30 Day TBill TR "], axis=1
        # )
        yearly_df = (
            subset_data.drop(["Period", "U.S. 30 Day TBill TR "], axis=1)
            .assign(
                Year=lambda x: x["Date"].apply(lambda x: x.split("-")[0]),
            )
            .drop("Date", axis=1)
            .groupby("Year")
            .mean()
            .reset_index()
            .drop("Year", axis=1)
        )
        fig1 = px.imshow(
            yearly_df.corr(),  # You can use df.corr() to compute the correlation matrix
            x=yearly_df.columns,
            y=yearly_df.columns,
            # zmin=-1,  # Set the color scale range from -1 to 1 for correlation values
            # zmax=1,
            color_continuous_scale="RdBu_r",
            text_auto=True,  # Choose a color scale    e the correlation matrix as text annotations
            labels=dict(color="Correlation"),
        )

        fig1.update_layout(title="Heatmap of Correlation Matrix")
        fig1.update_coloraxes(showscale=False)
        st.plotly_chart(fig1)
    with col2:
        fig2 = px.imshow(
            yearly_df.cov(),  # You can use df.corr() to compute the correlation matrix
            x=yearly_df.columns,
            y=yearly_df.columns,
            # zmin=0,  # Set the color scale range from -1 to 1 for correlation values
            # zmax=0.5,
            color_continuous_scale="Viridis",
            text_auto=True,  # Choose a color scale    e the correlation matrix as text annotations
            labels=dict(color="Covariance"),
        )

        fig2.update_layout(title="Heatmap of Covariance Matrix")
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2)

with tab3:
    expected_returns = (
        subset_data.drop(["Date", "Period", "U.S. 30 Day TBill TR "], axis=1).mean()
        * 12
    )

    cov_matrix = yearly_df.cov()
    target_mean_returns = cfg["periods"][time_range]
    efficient_set = minimize_std(expected_returns, cov_matrix, target_mean_returns)
    columns_to_format = [
        "Russell 2000 TR ",
        "S&P 500 TR ",
        "LB LT Gvt/Credit TR ",
        "MSCI EAFE TR ",
    ]
    st.subheader("2. Optimal Asset Allocation")
    st.dataframe(efficient_set.sort_values(by="min_std_dev"), use_container_width=True)
    st.divider()
    x_scale = alt.Scale(
        domain=[
            0,
            efficient_set["min_std_dev"].max() + 0.5,
        ]
    )  # Replace min_value_x and max_value_x with your desired limits for the x-axis
    y_scale = alt.Scale(
        domain=[
            0,
            efficient_set["target_mean_returns"].max() + 1,
        ]
    )
    chart = (
        alt.Chart(efficient_set)
        .mark_circle(size=60)
        .encode(
            x=alt.X(
                "min_std_dev",
                scale=x_scale,
                axis=alt.Axis(title="Anualized Volatility", tickCount=5),
            ),  # Set the custom X-axis label
            y=alt.Y(
                "target_mean_returns",
                scale=y_scale,
                axis=alt.Axis(title="Anualized Expected Return", tickCount=5),
            ),  # Set the custom Y-axis label
            tooltip=efficient_set.columns.tolist(),
            # color=alt.Color("Sharpe_Ratio:Q"),
            color=alt.Color(
                "Sharpe_Ratio:Q",
                scale=alt.Scale(range=["orange", "red", "blue"]),
            ),
        )
        .properties(
            width=600, height=500, title="Efficient Frontier Set"  # Set the width
        )  # Set the chart title
        .interactive()
    )

    tangent_df = find_tangent_line(efficient_set, subset_data)
    line_chart = (
        alt.Chart(tangent_df)  # Replace 'your_line_data' with your actual line data
        .mark_line(color="red", strokeDash=[5, 5])  # Use 'mark_line' for a line chart
        .encode(
            x=alt.X(
                "tangent_x",  # Replace with your X-axis field  # Customize X-axis label
            ),
            y=alt.Y(
                "tangent_y",  # Replace with your Y-axis field  # Customize Y-axis label
            ),
        )
    )
    st.altair_chart(chart + line_chart, theme="streamlit", use_container_width=True)

with tab4:
    st.subheader("3. Optimal Asset Allocation")
    st.text("")
    asset_class_df = generate_asset_class_df(cfg, efficient_set, wealth=1000000)
    st.dataframe(asset_class_df, use_container_width=True)
    st.caption(
        "The table above shows the optimal asset allocation (in dollars) for each asset class"
    )
    st.divider()
    st.markdown(f"<h5>Formula: </h5>", unsafe_allow_html=True)
    st.latex(portfolio_return_latex)
    st.latex(portfolio_risk_latex)
    st.divider()
    portfolio_return_df = calculate_agg_portfolio_return(
        subset_data, efficient_set, cfg
    )
    portfolio_risk_df = calculate_agg_portfolio_risk(yearly_df, efficient_set, cfg)
    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(portfolio_return_df, use_container_width=True)
    with col4:
        st.dataframe(portfolio_risk_df, use_container_width=True)
    st.caption(
        "Remark: They are all investing in the tangency portfolio with the same weights for the risky assets, thus the composition is the same."
    )
    st.divider()
    st.markdown(
        f"<h5>Group Average Risk Profile: {risk_value}</h5>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"- Allocation to risky assets: {risk_value*100}%", unsafe_allow_html=True
    )
    st.markdown(
        f"- Allocation to risk free assets: {(1-risk_value)*100}%",
        unsafe_allow_html=True,
    )
    group_profile = generate_group_asset_class_df(
        risk_value, subset_data, efficient_set, wealth=1000000
    )
    st.text("")
    st.dataframe(group_profile, use_container_width=True)

with tab5:
    uploaded_file = st.file_uploader("Choose a file", type="csv")
