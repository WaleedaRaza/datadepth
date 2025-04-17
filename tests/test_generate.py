from datadepth.profiler import profile_csv, save_schema
from datadepth.generator import generate_from_schema
import pandas as pd
from tempfile import NamedTemporaryFile

def test_generate_rows():
    df = pd.DataFrame({"age": [20, 30, 40], "color": ["red", "blue", "blue"]})
    with NamedTemporaryFile(suffix=".csv") as tmp_csv, NamedTemporaryFile(suffix=".json") as tmp_schema:
        df.to_csv(tmp_csv.name, index=False)
        schema = profile_csv(tmp_csv.name)
        save_schema(schema, tmp_schema.name)

        synth = generate_from_schema(tmp_schema.name, 50)
        assert len(synth) == 50
        assert set(synth.columns) == {"age", "color"}
