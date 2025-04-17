# DataDepth
# DataDepth

> **Synthetic data that *looks* like the real thing — in one command.**
>
> `datadepth` turns any tabular CSV into a privacy‑safe, schema‑aware, statistically‑plausible dataset.  Perfect for demos, CI pipelines, tutorials and exploratory data‑science.

---

## ✨ Key features

| Capability | What it does | CLI flag |
|------------|-------------|----------|
| **Smart profiling** | Infers column types (numeric, datetime, categorical, free‑text) & stats. | `datadepth profile` |
| **Header detection** | `--no-header` flag for raw dumps / exports without column names. | `--no-header` |
| **Schema JSON** | Portable description of your dataset, saved to `schema.json` (or custom). | `-s / --schema` |
| **Synthetic generation** | Produces deterministic, statistically‑similar rows on demand. | `datadepth generate` |
| **Preview** | Quick 5‑row sample of any schema. | `datadepth preview` |
| **Validation** | Checks a schema file for completeness. | `datadepth validate` |

---

## 🚀 Quick‑start (TL;DR)

```bash
# 1. Install (inside an activated venv)
python -m pip install datadepth  # or `pip install -e .` when developing

# 2. Profile a CSV WITH headers
$ datadepth profile NVIDIA_STOCK.csv -s nvidia_schema.json

# 3. Profile a CSV WITHOUT headers
$ datadepth profile twitter_training.csv --no-header -s twitter_schema.json

# 4. Generate 10k synthetic rows
$ datadepth generate nvidia_schema.json -n 10000 -o fake_nvidia.csv

# 5. Peek at a schema
$ datadepth preview twitter_schema.json
```

---

## 🛠  CLI reference

### `datadepth profile <input_csv>`
Profiles a CSV and writes a schema.

```
Options:
  -s, --schema TEXT    Path to save schema (default: schema.json)
  --no-header          Treat first row as data, auto‑create col_0 … col_N.
  -q, --quiet          Suppress progress output.
```

### `datadepth generate <schema.json>`
Generates synthetic rows from a schema.

```
Options:
  -n, --num-rows INTEGER  Rows to generate (default: 1000)
  -o, --out TEXT          CSV output path (default: synthetic.csv)
```

### `datadepth preview <schema.json>`
Prints five synthetic rows to stdout.

### `datadepth validate <schema.json>`
Verifies that a schema file is complete and well‑formed.

---

## 🧑‍💻  Developer setup

```bash
# clone
$ git clone https://github.com/<your-user>/datadepth.git && cd datadepth

# poetry for deps & virtualenv
$ poetry install --with dev
$ poetry shell   # activate venv

# run tests
$ pytest

# run the CLI from source
$ datadepth --help
```

### Pre‑commit hooks

```bash
$ pre-commit install   # auto‑formats & lints on each commit
```

---

## 📈  Project status

* **v1** (current): working numeric / categorical / datetime sampler, header detection, CLI flags.
* **v2 (WIP):**
  - Per‑column strategy plugins (Gaussian, KDE, Markov for text)
  - ML‑based mixed‑type generator
  - YAML config overrides
  - PyPI release & Homebrew tap

---

## 🗺️  Roadmap

1. **Robust profiler** – smarter type inference, outlier handling.
2. **Pluggable generators** – users can register custom sampling functions.
3. **CLI UX polish** – colored output, human‑readable table preview.
4. **Docs site** – mkdocs‑material, recipe gallery.
5. **Cloud mode** – optional web API + hosted dataset vault.

---

## 🤝  Contributing

PRs & issues welcome!  Please run `pre-commit run --all-files` and make sure `pytest` is green before pushing.

---

## ⚙️  Git workflow cheatsheet

```bash
# one‑time
$ git config --global user.name  "Your Name"
$ git config --global user.email "you@example.com"

# day‑to‑day
$ git checkout -b feat/<brief‑slug>      # start new work
# …edit code…
$ git add -A && git commit -m "feat: <what & why>"
$ git push -u origin feat/<slug>

# keep branch fresh
$ git pull --rebase origin main

# merge back (fast‑forward preferred)
$ git checkout main
$ git pull
$ git merge --ff-only feat/<slug>
$ git push
```

---

## 📝  License

 © 2025 Waleed Raza
