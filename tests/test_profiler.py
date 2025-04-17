import pandas as pd
from datadepth.profiler import Profiler


def test_generate_profile():
    df = pd.DataFrame({"x": [1, 2, 3]})
    profile = Profiler(df).profile()
    assert profile["num_rows"] == 3
