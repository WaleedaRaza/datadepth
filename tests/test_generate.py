# tests/test_generate.py

import pandas as pd
from tempfile import NamedTemporaryFile
from datadepth.profiler import Profiler
from datadepth.synthesizer import generate_rows, save_rows


def test_generate_rows():
    df = pd.DataFrame({"age": [20, 30, 40], "color": ["red", "blue", "blue"]})

    with (
        NamedTemporaryFile(suffix=".csv") as tmp_csv,
        NamedTemporaryFile(suffix=".json") as tmp_schema,
        NamedTemporaryFile(suffix=".csv") as tmp_output,
    ):
        df.to_csv(tmp_csv.name, index=False)

        schema = Profiler(pd.read_csv(tmp_csv.name)).profile()
        df_gen = generate_rows(schema, 100)
        save_rows(df_gen, tmp_output.name)

        df_out = pd.read_csv(tmp_output.name)
        assert df_out.shape[0] == 100
