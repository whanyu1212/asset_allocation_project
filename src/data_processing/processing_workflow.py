import pandas as pd
import datetime
import glob
import os
import warnings

warnings.filterwarnings("ignore")
from prefect import flow, task


@task(task_run_name="Process raw xlsx files")
def process_raw_xlsx_files(df: pd.DataFrame) -> pd.DataFrame:
    """Process the raw data in xlsx files
       and store them in proper dataframes.
       Assign a column called Period to
       indicate the time period of the data.

    Args:
        df (pd.DataFrame): dataframe read in from xlsx files

    Returns:
        pd.Dataframe: cleaned dataframe
    """

    # Replace column names
    headers = df.dropna(how="all", axis=1).iloc[2].values.tolist()

    # Drop missing values by filter values other than datetime in the column
    df_cleaned = (
        df.dropna(how="all", axis=1)
        .set_axis(headers, axis=1)
        .assign(Date=lambda x: pd.to_datetime(x["Date"], errors="coerce"))
        .dropna(subset=["Date"])
        .reset_index(drop=True)
    )

    # Convert the remaining columns to float
    df_final = pd.concat(
        [
            df_cleaned[["Date"]],
            df_cleaned.drop("Date", axis=1).apply(
                pd.to_numeric, errors="coerce", downcast="float"
            )
            * 100,
        ],
        axis=1,
    ).assign(Period=lambda x: str(x["Date"].dt.year.min() // 10 * 10) + "s")

    return df_final


@flow(flow_run_name="Process raw data for multiple time periods")
def process_raw_data_for_multiple_time_periods(directory_path: str) -> None:
    overall_df = pd.DataFrame()  # Initialize an empty dataframe
    file_paths = glob.glob(os.path.join(directory_path, "*"))
    for path in file_paths:
        temp_df = pd.read_excel(path, sheet_name="Data")
        temp_df_processed = process_raw_xlsx_files(temp_df)
        overall_df = pd.concat([overall_df, temp_df_processed], axis=0)
    overall_df.columns = overall_df.columns.str.strip()
    overall_df.to_csv("./data/processed/processed_data.csv", index=False)


if __name__ == "__main__":
    directory_path = "./data/raw"
    process_raw_data_for_multiple_time_periods(directory_path)
