"""Summarize neuronal unit quality and export unit-level CSV tables."""

from pathlib import Path

import h5py
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
FILE_PATTERN = "*processed_behavior+ecephys.nwb"


def find_nwb_file() -> Path:
    """Locate the single processed NWB file used in the analysis."""
    files = sorted(DATA_DIR.glob(FILE_PATTERN))
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly one processed NWB file in {DATA_DIR}; "
            f"found {len(files)}."
        )
    return files[0]


def load_unit_table(file_path: Path) -> pd.DataFrame:
    """Load unit identifiers, firing rates, spike counts, and quality labels."""
    with h5py.File(file_path, "r") as file:
        units = file["units"]
        raw_labels = units["kilosort2_label"][:]
        labels = [
            value.decode("utf-8") if isinstance(value, bytes) else str(value)
            for value in raw_labels
        ]
        return pd.DataFrame(
            {
                "unit_id": units["id"][:],
                "firing_rate_hz": units["firing_rate"][:],
                "spike_count": units["spike_count"][:],
                "quality_label": labels,
            }
        )


def main() -> None:
    """Print descriptive statistics and export all and good-quality units."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    units = load_unit_table(find_nwb_file())
    good_units = units.loc[units["quality_label"] == "good"].copy()

    print("=" * 55)
    print("NEURONAL UNIT QUALITY ANALYSIS")
    print("=" * 55)
    print(f"\nTotal units: {len(units)}")
    print(f"Good-quality units: {len(good_units)}")
    print(f"Multi-unit activity (MUA): {(units['quality_label'] == 'mua').sum()}")
    print("\nFiring-rate statistics for good-quality units:")
    print(good_units["firing_rate_hz"].describe())
    print("\nSpike counts by quality label:")
    print(units.groupby("quality_label")["spike_count"].sum())

    units.to_csv(RESULTS_DIR / "neurons_all.csv", index=False)
    good_units.to_csv(RESULTS_DIR / "neurons_good.csv", index=False)
    print("\nCSV files exported to results/.")
    print("Unit analysis completed.")


if __name__ == "__main__":
    main()
