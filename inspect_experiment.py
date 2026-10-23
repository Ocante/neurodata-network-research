"""Inspect neuronal units, behavioral data, and spike timing in an NWB file."""

from pathlib import Path

import h5py
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FILE_PATTERN = "*processed_behavior+ecephys.nwb"


def find_nwb_file() -> Path:
    """Find the single processed NWB file used by this project."""
    files = sorted(DATA_DIR.glob(FILE_PATTERN))
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly one processed NWB file in {DATA_DIR}; "
            f"found {len(files)}."
        )
    return files[0]


def show_group(group: h5py.Group, limit: int = 50) -> None:
    """Display names and shapes of a limited number of group members."""
    for name, item in list(group.items())[:limit]:
        shape = getattr(item, "shape", "group")
        print(f"  {name}: {shape}")


def summarize_spike_times(dataset: h5py.Dataset) -> None:
    """Find the global spike-time range without loading all spikes into memory."""
    if len(dataset) == 0:
        print("No spike times available.")
        return

    minimum = float("inf")
    maximum = float("-inf")
    block_size = 1_000_000

    for start in range(0, len(dataset), block_size):
        block = dataset[start : start + block_size]
        finite = block[np.isfinite(block)]
        if finite.size:
            minimum = min(minimum, float(np.min(finite)))
            maximum = max(maximum, float(np.max(finite)))

    if np.isfinite(minimum) and np.isfinite(maximum):
        print(f"First recorded spike: {minimum:.3f} s")
        print(f"Last recorded spike: {maximum:.3f} s")
        print(f"Spike-time span: {maximum - minimum:.3f} s")
    else:
        print("No finite spike times found.")


def main() -> None:
    """Summarize electrophysiology and behavioral metadata."""
    file_path = find_nwb_file()
    print("=" * 65)
    print("NEURODATA - EXPERIMENT INSPECTION")
    print("=" * 65)
    print(f"File: {file_path.name}")

    with h5py.File(file_path, "r") as file:
        if "units" not in file:
            raise KeyError("The NWB file does not contain a 'units' group.")
        units = file["units"]

        print("\n1. NEURONAL UNITS")
        show_group(units, limit=40)
        print(f"\nTotal units: {len(units['id'])}")

        if "firing_rate" in units:
            rates = units["firing_rate"][:]
            finite = rates[np.isfinite(rates)]
            if finite.size:
                print(f"Mean firing rate: {np.mean(finite):.3f} Hz")
                print(f"Median firing rate: {np.median(finite):.3f} Hz")

        if "ibl_quality_score" in units:
            scores = units["ibl_quality_score"][:]
            print("\nIBL quality scores:")
            print(f"  Data type: {scores.dtype}")
            print(f"  First values: {scores[:10]}")

        if "kilosort2_label" in units:
            raw_labels = units["kilosort2_label"][:]
            labels = [
                value.decode("utf-8") if isinstance(value, bytes) else str(value)
                for value in raw_labels
            ]
            unique, counts = np.unique(labels, return_counts=True)
            print("\nKilosort2 quality labels:")
            for label, count in zip(unique, counts):
                print(f"  {label}: {count}")

        print("\n2. BEHAVIORAL TRIALS")
        if "intervals/trials" in file:
            trials = file["intervals/trials"]
            show_group(trials, limit=60)
            if "id" in trials:
                print(f"Total trials: {len(trials['id'])}")
        else:
            print("No trials group found.")

        print("\n3. BEHAVIORAL PROCESSING DATA")
        if "processing" in file:
            for name, item in file["processing"].items():
                print(f"\n{name}:")
                if isinstance(item, h5py.Group):
                    show_group(item, limit=30)
        else:
            print("No processing group found.")

        print("\n4. GLOBAL SPIKE-TIME RANGE")
        if "spike_times" in units:
            summarize_spike_times(units["spike_times"])
        else:
            print("No spike_times dataset found.")

    print("\nExperiment inspection completed.")


if __name__ == "__main__":
    main()
