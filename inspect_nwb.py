"""Inspect the top-level structure of a processed NWB dataset."""

from pathlib import Path

import h5py

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FILE_PATTERN = "*processed_behavior+ecephys.nwb"


def find_nwb_file() -> Path:
    """Return the single processed NWB file in the data directory."""
    files = sorted(DATA_DIR.glob(FILE_PATTERN))
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly one processed NWB file in {DATA_DIR}; "
            f"found {len(files)}."
        )
    return files[0]


def inspect_group(file: h5py.File, path: str, limit: int = 30) -> None:
    """Print a concise listing of a group or dataset."""
    print(f"\n--- {path} ---")
    if path not in file:
        print("Not found at this path.")
        return

    obj = file[path]
    if isinstance(obj, h5py.Group):
        for name, item in list(obj.items())[:limit]:
            shape = getattr(item, "shape", "group")
            print(f"  {name}: {shape}")
    else:
        print(f"Dataset shape: {obj.shape}")


def main() -> None:
    """Display the NWB hierarchy and selected electrophysiology groups."""
    file_path = find_nwb_file()
    print("=" * 65)
    print("NEURODATA NETWORK RESEARCH - NWB STRUCTURE INSPECTION")
    print("=" * 65)
    print(f"File: {file_path.name}")

    with h5py.File(file_path, "r") as file:
        print("\nTOP-LEVEL GROUPS")
        for name in file.keys():
            print(f"  - {name}")

        for path in (
            "units",
            "acquisition",
            "processing",
            "intervals",
            "electrodes",
            "general/extracellular_ephys",
        ):
            inspect_group(file, path)

    print("\nNWB structure inspection completed.")


if __name__ == "__main__":
    main()
