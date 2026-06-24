from polars_csv_explorer.explore import INPUT_CSV, load, explore, transform, write


def main() -> None:
    df = load(INPUT_CSV)
    explore(df)
    df = transform(df)
    write(df)


if __name__ == "__main__":
    main()
