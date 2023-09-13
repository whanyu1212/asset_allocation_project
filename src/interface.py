import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pandas_profiling
import tempfile
import plotly.express as px
from streamlit_pandas_profiling import st_profile_report
from pandas_profiling import ProfileReport
from util.basic_utility import (
    highlight_max_by_column,
    highlight_min_by_column,
    parse_config,
)
from util.latex_formula import (
    latex_formula_monthly_annual,
    portfolio_return_latex,
    portfolio_risk_latex,
)

from util.functions_by_tab.tab4 import (
    generate_asset_class_df,
    generate_group_asset_class_df,
    calculate_agg_portfolio_return,
    calculate_agg_portfolio_risk,
)


from util.functions_by_tab.tab1 import create_line_chart
from util.functions_by_tab.tab2 import (
    geo_mean,
    plot_corr_heatmap_by_month,
    plot_corr_heatmap_by_year,
    generate_monthly_n_annual_stats_df,
    generate_yearly_df_stats,
)
from util.functions_by_tab.tab3 import (
    generate_efficient_frontier_plot,
    trust_region_solver,
    find_tangent_line,
)
from util.functions_by_tab.tab5 import get_qna_ans

# Global configurations for UI
st.set_page_config(layout="wide")
st.title("Navigating Asset Allocation")

# Global variables
data = pd.read_csv("./data/processed/processed_data.csv")

numeric_columns = data.select_dtypes(include="number").columns.tolist()

cfg = parse_config("./cfg/config.yml")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        ":bar_chart: Exploratory Analysis",
        ":pencil2: Statistics for Question 1",
        ":chart: Efficient Frontier",
        ":money_with_wings: Optimal Capital Allocation",
        ":speech_balloon: Chat with your data",
    ]
)

################################################################################################################################################
# Sidebar configuration
with st.sidebar:
    header = st.header("Configurations :gear:")

    st.divider()

    time_range = st.radio(
        ":calendar: Choose the period of time you want to analyze:",
        sorted(cfg["periods"].keys()),
        captions=["High Inflation", "The equity market bull-run", "Financial Crisis"],
    )

    st.text("")  # using this as divider but without the line

    indexes_options = st.multiselect(
        " :mag_right: Zoom into the specific indexes:",
        cfg["indexes_options"],
        cfg["indexes_options"],
    )

    st.text("")

    risk_value = st.slider(
        ":bust_in_silhouette: User defined weightage for risky assets", 0.0, 1.0, 0.5
    )

    st.text("")

    # Add a link to the github repo
    link = ":point_right: Github Repository for the dashboard: [link](https://github.com/whanyu1212/asset_allocation_project)"
    st.markdown(link, unsafe_allow_html=True)
    st.text("")
    link_solver = ":point_right: Documentation for the solver: [link](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html#optimize-minimize-trustconstr)"
    st.markdown(link_solver, unsafe_allow_html=True)
################################################################################################################################################
# Tab 1: Exploratory Analysis
with tab1:
    subset_data = data[data["Period"] == time_range]

    # st.markdown(f"**Summary Statistics for {time_range}:**", unsafe_allow_html=True)

    pr = subset_data.profile_report()

    st_profile_report(pr)

    # Display the summary statistics as a dataframe
    # st.dataframe(subset_data.describe(), use_container_width=True)

    st.divider()


################################################################################################################################################
# Tab 2: Calculations for question 1
with tab2:
    st.markdown(f"**Time Series Plot for {time_range}:**", unsafe_allow_html=True)

    # Pivot the df so we can a grouped line chart by indexes
    subset_data_pivot = (
        pd.melt(
            subset_data.drop("Period", axis=1),
            id_vars="Date",
            var_name="Indexes",
            value_name="Value",
        )
        .sort_values(by=["Date", "Indexes"])
        .query("Indexes in @indexes_options")
    )

    # Call the function to generate a line chart
    create_line_chart(subset_data_pivot)
    st.divider()

    # Display the formula for the aggregated statistics
    st.markdown(f"**Formula for aggregated statistics:**", unsafe_allow_html=True)
    st.latex(latex_formula_monthly_annual)
    st.divider()

    st.markdown("**Monthly and Annual Average Return and Standard Deviation:**")
    st.text("")
    # Call the function to generate a dataframe to store the monthly and annual aggregated statistics
    yearly_df = generate_yearly_df_stats(subset_data)
    generate_monthly_n_annual_stats_df(subset_data, yearly_df)

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        plot_corr_heatmap_by_month(subset_data, cfg)
    with col2:
        plot_corr_heatmap_by_year(yearly_df, cfg)


################################################################################################################################################

with tab3:
    st.markdown("**Optimal Asset Allocation:**")

    # Expected return of the risky assets
    expected_returns = (
        subset_data.drop(["Date", "Period", cfg["risk_free_asset"]], axis=1).mean() * 12
    )

    # cov_matrix = subset_data.drop(
    #     ["Date", "Period", cfg["risk_free_asset"]], axis=1
    # ).cov()

    # expected_returns = yearly_df.drop(["Year"], axis=1).mean()
    cov_matrix = np.array(
        yearly_df.drop(["Year", cfg["risk_free_asset"]], axis=1).cov()
    )

    # List of pre-defined target mean returns
    target_mean_returns = cfg["periods"][time_range]

    efficient_set = trust_region_solver(
        expected_returns, cov_matrix, target_mean_returns
    )

    # Generate the dataframe that stores weights and portfolio mean returns
    # Color the minimum standard deviation and maximum Sharpe Ratio
    st.dataframe(
        efficient_set.style.highlight_min(
            axis=0, props="background-color:LightGreen;", subset=["min_std_dev"]
        ).highlight_max(
            axis=0, props="background-color:LightCoral;", subset=["Sharpe_Ratio"]
        ),
        use_container_width=True,
    )
    st.caption(
        "Remark: The allocation weights for each asset class are determined through the application of the trust region method.\
        The minimum standard deviation is highlighted in green and the maximum Sharpe is highlighted in coral."
    )
    st.divider()

    # Plot the curve and the tangential line
    x_scale = alt.Scale(
        domain=[
            0,
            efficient_set["min_std_dev"].max() + 0.5,
        ]
    )
    y_scale = alt.Scale(
        domain=[
            0,
            efficient_set["target_mean_returns"].max() + 1,
        ]
    )

    tangent_df = find_tangent_line(efficient_set, subset_data, cfg)
    generate_efficient_frontier_plot(efficient_set, x_scale, y_scale, tangent_df)

################################################################################################################################################
# Tab 4: Calculations for optimal capital allocation
with tab4:
    st.markdown("**Optimal Capital Allocation:**")
    st.text("")
    # Dataframe that stores the dollar amount allocated to each asset class based on the optimal weight calculated
    asset_class_df = generate_asset_class_df(cfg, efficient_set, wealth=1000000)
    st.dataframe(asset_class_df, use_container_width=True)
    st.caption(
        "The table above shows the optimal capital allocation (in dollars) for each asset class"
    )
    st.divider()
    # Use latex to display the formula
    st.markdown(f"<h6>Formula: </h6>", unsafe_allow_html=True)
    # Latex formula
    st.latex(portfolio_return_latex)
    st.latex(portfolio_risk_latex)
    st.divider()
    # Dataframe that stores the portfolio return and risk for each investor
    portfolio_return_df = calculate_agg_portfolio_return(
        subset_data, efficient_set, cfg
    )
    portfolio_risk_df = calculate_agg_portfolio_risk(cov_matrix, efficient_set, cfg)
    col3, col4 = st.columns(2)
    with col3:
        st.dataframe(portfolio_return_df, use_container_width=True)
    with col4:
        st.dataframe(portfolio_risk_df, use_container_width=True)
    st.caption(
        "Remark: They are all investing in the tangency portfolio with the same weights for the risky assets, thus the composition is the same."
    )
    st.divider()
    # Dynamic value based on the slider in the sidebar
    st.markdown(
        f"<h6>Group Average Risk Profile: {risk_value}</h6>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"- Allocation to risky assets: {risk_value*100}%", unsafe_allow_html=True
    )
    st.markdown(
        f"- Allocation to risk free assets: {(1-risk_value)*100}%",
        unsafe_allow_html=True,
    )
    # Dollar investment for each asset class based on the weightage chosen in the slider
    group_profile = generate_group_asset_class_df(
        cfg, risk_value, subset_data, efficient_set, wealth=1000000
    )
    st.text("")
    st.dataframe(group_profile, use_container_width=True)

with tab5:
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type="csv")
    # If something is uploaded, read it into a pd dataframe
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            csv_path = tmp_file.name
            df = pd.read_csv(csv_path)
            if df.empty == False:
                st.success("File uploaded successfully!")
            if st.checkbox("Show raw data"):
                st.dataframe(df, use_container_width=True)
            st.text("")
            question = st.text_input(
                "**Chat with your data**",
                value="""Enter your question here...""",
            )

            if question != """Enter your question here...""":
                with st.spinner(text="Retrieving answer in progress..."):
                    get_qna_ans(df, question)
    else:
        st.warning(
            "Please upload a non-empty csv file before you can start chatting with the data",
            icon="⚠️",
        )
