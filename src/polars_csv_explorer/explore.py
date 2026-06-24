"""
Polars CSV Explorer
-------------------
Load, explore, filter, and write CSV datasets using Polars.
"""

import polars as pl
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration – change these paths as needed
# ---------------------------------------------------------------------------
INPUT_CSV = Path("data/sample.csv")  # path to your CSV file (or glob)
OUTPUT_DIR = Path("output")  # directory to write results
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------
def load(path: Path) -> pl.DataFrame:
    """Load a single CSV file."""
    return pl.read_csv(path, infer_schema_length=1000)


def load_many(glob: str) -> pl.DataFrame:
    """Load and stack multiple CSVs matching a glob pattern, e.g. 'data/*.csv'."""
    frames = [pl.read_csv(p) for p in sorted(Path(".").glob(glob))]
    return pl.concat(frames, rechunk=True)


# ---------------------------------------------------------------------------
# 2. Explore
# ---------------------------------------------------------------------------
def explore(df: pl.DataFrame) -> None:
    print("=== Shape ===")
    print(f"  rows: {df.height:,}  cols: {df.width}")

    print("\n=== Schema ===")
    for col, dtype in df.schema.items():
        print(f"  {col:<30} {dtype}")

    print("\n=== Head (5 rows) ===")
    print(df.head(5))

    print("\n=== Describe ===")
    print(df.describe())

    print("\n=== Null counts ===")
    print(df.null_count())


# ---------------------------------------------------------------------------
# 3. Example transforms – customise to your data
# ---------------------------------------------------------------------------
def transform(df: pl.DataFrame) -> pl.DataFrame:
    # --- Drop fully-empty columns ---
    df = df[[c for c in df.columns if df[c].null_count() < df.height]]

    # --- Cast a column to numeric (example) ---
    # df = df.with_columns(pl.col("price").cast(pl.Float64))

    # --- Filter rows (example) ---
    # df = df.filter(pl.col("status") == "active")

    # --- Rename columns to snake_case (example) ---
    # df = df.rename({c: c.lower().replace(" ", "_") for c in df.columns})

    # --- Add a derived column (example) ---
    # df = df.with_columns((pl.col("qty") * pl.col("price")).alias("total"))

    # --- Group-by aggregation (example) ---
    # summary = df.group_by("category").agg(
    #     pl.col("total").sum().alias("total_sales"),
    #     pl.col("id").count().alias("count"),
    # )
    # summary.write_csv(OUTPUT_DIR / "summary.csv")

    return df


# ---------------------------------------------------------------------------
# 4. Write output
# ---------------------------------------------------------------------------
def write(df: pl.DataFrame, stem: str = "result") -> None:
    # CSV
    csv_path = OUTPUT_DIR / f"{stem}.csv"
    df.write_csv(csv_path)
    print(f"\nWrote CSV     -> {csv_path}")

    # Parquet (fast, compressed, preserves types)
    parquet_path = OUTPUT_DIR / f"{stem}.parquet"
    df.write_parquet(parquet_path, compression="zstd")
    print(f"Wrote Parquet -> {parquet_path}")

    # JSON lines (optional)
    # jsonl_path = OUTPUT_DIR / f"{stem}.jsonl"
    # df.write_ndjson(jsonl_path)
    # print(f"Wrote NDJSON  -> {jsonl_path}")


# ---------------------------------------------------------------------------
# 5. Re-load from parquet example
# ---------------------------------------------------------------------------
def reload_parquet(stem: str = "result") -> pl.DataFrame:
    return pl.read_parquet(OUTPUT_DIR / f"{stem}.parquet")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # --- create a tiny synthetic CSV if no real file exists yet ---
    if not INPUT_CSV.exists():
        INPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        sample = pl.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
                "score": [88.5, 72.0, 95.3, None, 61.8],
                "category": ["A", "B", "A", "C", "B"],
            }
        )
        sample.write_csv(INPUT_CSV)
        print(f"Created sample CSV at {INPUT_CSV}\n")

    df = load(INPUT_CSV)

    print(">>> RAW DATA")
    explore(df)

    df = transform(df)

    print("\n>>> AFTER TRANSFORM")
    print(df)

    write(df)

    # Verify round-trip
    df2 = reload_parquet()
    print(f"\nReloaded parquet: {df2.height} rows, {df2.width} cols")
