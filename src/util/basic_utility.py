import yaml
import pandas as pd
import numpy as np


# Helper functions
# def highlight_max_by_column(s):
#     is_max = s == s.max()
#     return ["background-color: LightCoral" if v else "" for v in is_max]


def highlight_max_by_column(s):
    if s.dtype in (int, float):
        is_max = s == s.max()
        return ["background-color: RoyalBlue" if v else "" for v in is_max]
    else:
        return ["" for _ in s]


def highlight_min_by_column(s):
    is_min = s == s.min()
    return ["background-color: LightBlue" if v else "" for v in is_min]


def parse_config(path):
    with open(path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
