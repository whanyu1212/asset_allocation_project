<h1>Asset Allocation Project</h1>
<h3>Folder structure:</h3>
```
|-- .streamlit|
|   |-- secrets.toml
|-- cfg|
|   |-- config.yml
|-- data
|   |-- processed
|       |-- processed_data.csv
|   |-- raw
|       |-- Project1-AssetAllocation-1980s_template.xlsx
|       |-- Project1-AssetAllocation-1990s_template.xlsx
|       |-- Project1-AssetAllocation-2000s_template.xlsx
|-- notebooks
|   |-- scratchpad.ipynb
|-- src
|   |-- data_processing
|       |-- processing_workflow.py
|   |-- util
|       |-- functions_by_tab
|           |-- tab1.py
|           |-- tab2.py
|           |-- tab3.py
|           |-- tab4.py
|           |-- tab5.py
|       |-- basic_utility.py
|       |-- latex_formula.py
|   |-- interface.py
|-- tests
|-- .gitignore
|-- .python-version
|-- poetry.lock
|-- pyproject.toml
|-- README.md
```
<h3> Simple Workflow Diagram </h3>

```mermaid
flowchart LR
  subgraph TABS
    direction TB
    subgraph EDA
        direction LR
        Pandas_profiling
    end
    subgraph Calculating_Statistics
        direction TB
        Timeseries -->Monthly_n_annual_statistics -->Correlation_matrix
    end
    subgraph Efficient_Frontier
        direction TB
        Optimization -->Efficient_set_plot
    end
    subgraph Optimal_Capital_Allocation
        direction TB
        Calculate_dollar_investment -->Group_risk_profile
    end
  end
  DATA_PROCESSING --> TABS --> STREAMLIT_INTERFACE
  
```
