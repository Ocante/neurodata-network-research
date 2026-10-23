"""Build an exploratory spike-count correlation network from NWB units.

The graph is undirected. Edges represent absolute Pearson correlations
at or above the configured threshold; they do not establish anatomical
connections or causal relationships.
"""

from pathlib import Path

import h5py
import networkx as nx
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
FILE_PATTERN = "*processed_behavior+ecephys.nwb"

BIN_SIZE_SECONDS = 1.0
CORRELATION_THRESHOLD = 0.30


def find_nwb_file() -> Path:
    """Return the single processed NWB file used by this project."""
    files = sorted(DATA_DIR.glob(FILE_PATTERN))
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly one processed NWB file in {DATA_DIR}; "
            f"found {len(files)}."
        )
    return files[0]


def load_spike_count_matrix(file_path: Path) -> tuple[list[int], np.ndarray, float]:
    """Bin spikes from Kilosort2 'good' units into one-second intervals.

    The time axis begins at zero and ends after the last spike among
    selected units. This is not necessarily the experiment's full duration.
    """
    with h5py.File(file_path, "r") as file:
        units = file["units"]
        ids = units["id"][:]
        labels = [
            value.decode("utf-8") if isinstance(value, bytes) else str(value)
            for value in units["kilosort2_label"][:]
        ]
        good_indices = np.flatnonzero(np.asarray(labels) == "good")
        spike_index = units["spike_times_index"][:]
        spike_data = units["spike_times"]

        last_spike_times = []
        for index in good_indices:
            start = 0 if index == 0 else int(spike_index[index - 1])
            end = int(spike_index[index])
            if end > start:
                last_spike_times.append(float(spike_data[end - 1]))

        if not last_spike_times:
            raise RuntimeError("No spikes found among good-quality units.")

        last_spike_time = max(last_spike_times)
        if not np.isfinite(last_spike_time) or last_spike_time < 0:
            raise ValueError("The selected spike-time range is invalid.")

        # Include the last selected spike in the final time bin.
        bins = np.arange(
            0,
            np.ceil(last_spike_time / BIN_SIZE_SECONDS) * BIN_SIZE_SECONDS
            + BIN_SIZE_SECONDS,
            BIN_SIZE_SECONDS,
        )
        matrix = np.zeros((len(good_indices), len(bins) - 1), dtype=np.float32)
        selected_ids = []

        for row, index in enumerate(good_indices):
            start = 0 if index == 0 else int(spike_index[index - 1])
            end = int(spike_index[index])
            spikes = spike_data[start:end]
            counts, _ = np.histogram(spikes, bins=bins)
            matrix[row] = counts
            selected_ids.append(int(ids[index]))

    return selected_ids, matrix, last_spike_time


def build_graph(unit_ids: list[int], correlation: np.ndarray) -> nx.Graph:
    """Connect units whose absolute Pearson correlation meets the threshold."""
    graph = nx.Graph()
    graph.add_nodes_from(unit_ids)

    for i, source in enumerate(unit_ids):
        for j in range(i + 1, len(unit_ids)):
            value = float(correlation[i, j])
            if np.isfinite(value) and abs(value) >= CORRELATION_THRESHOLD:
                graph.add_edge(
                    source,
                    unit_ids[j],
                    weight=abs(value),
                    correlation=value,
                )

    return graph


def export_results(graph: nx.Graph, correlation: np.ndarray) -> None:
    """Export the correlation matrix, network files, and edge list."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    np.save(RESULTS_DIR / "correlation_matrix.npy", correlation)
    nx.write_gexf(graph, RESULTS_DIR / "neural_network.gexf")
    nx.write_graphml(graph, RESULTS_DIR / "neural_network.graphml")

    edges = [
        {
            "source": source,
            "target": target,
            "weight": attributes["weight"],
            "correlation": attributes["correlation"],
        }
        for source, target, attributes in graph.edges(data=True)
    ]
    pd.DataFrame(
        edges, columns=["source", "target", "weight", "correlation"]
    ).to_csv(RESULTS_DIR / "neural_edges.csv", index=False)


def main() -> None:
    """Generate the network and report basic graph statistics."""
    unit_ids, matrix, last_spike_time = load_spike_count_matrix(find_nwb_file())
    print(f"Selected good-quality units: {len(unit_ids)}")
    print(f"Last selected spike (seconds): {last_spike_time:.6f}")
    print(f"Time bins: {matrix.shape[1]}")

    # Constant spike-count series have undefined Pearson correlation.
    valid = np.std(matrix, axis=1) > 0
    matrix = matrix[valid]
    unit_ids = [unit_id for unit_id, keep in zip(unit_ids, valid) if keep]
    if len(unit_ids) < 2:
        raise RuntimeError("At least two nonconstant spike-count series are required.")

    correlation = np.corrcoef(matrix)
    graph = build_graph(unit_ids, correlation)
    export_results(graph, correlation)

    components = list(nx.connected_components(graph))
    largest_component_size = max(map(len, components), default=0)

    print("\nNETWORK RESULTS")
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    print(f"Density: {nx.density(graph):.12f}")
    print(f"Connected components: {len(components)}")
    print(f"Largest connected component: {largest_component_size}")
    print("\nNetwork files exported to results/.")
    print("Processing completed successfully.")


if __name__ == "__main__":
    main()
