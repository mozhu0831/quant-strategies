from pathlib import Path

from compare import run_comparison
from download_data import download_price_data


def main():
    base_dir = Path(__file__).parent
    prices_path = base_dir / "prices.csv"

    if not prices_path.exists():
        download_price_data()

    out_dir = base_dir / "outputs"
    out_dir.mkdir(exist_ok=True)

    run_comparison(
        prices_path="prices.csv",
        eval_start="2020-01-02",
        eval_end="2025-12-31",
        save_fig=True,
    )


if __name__ == "__main__":
    main()
