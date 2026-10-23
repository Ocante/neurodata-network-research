# Methodology

## Research scope

This project demonstrates an exploratory computational workflow for turning extracellular neuronal spike timestamps from a single NWB session into a statistical association network. It is a graph-analysis project, not a trained artificial neural network or a causal connectivity estimator.

## 1. NWB inspection

The workflow uses `h5py` to read an NWB file with a name matching `*processed_behavior+ecephys.nwb` in `data/`. It inspects the `units`, `processing`, and `intervals/trials` groups. The inspected recording contains 519 units and 854 behavioral trials.

## 2. Unit quality selection

The `units/kilosort2_label` field labels 113 units `good` and 406 units `mua`. Only units labeled `good` are selected for network construction. These labels are supplied by the source processing pipeline; this project does not independently validate spike sorting.

## 3. Spike-train reconstruction

Spike timestamps are stored in the flattened `units/spike_times` array, with unit-specific boundaries in `units/spike_times_index`. Each selected unit is associated with its corresponding timestamp slice. The NWB `units/id` values identify nodes.

## 4. Temporal binning

Spike timestamps are counted in non-overlapping 1.0-second windows starting at time zero. The end of the analysis is determined from the latest spike among selected units, rounded up to a complete time bin. The observed final selected spike was approximately 5417.654249 seconds, producing 5,418 bins.

**Important:** This end point is the last selected spike, not independently verified session duration. Binning at one-second resolution discards sub-second temporal structure.

## 5. Pairwise correlation

For each pair of selected units, the workflow computes Pearson correlation between their binned spike-count series using NumPy. Constant series cannot yield a defined Pearson correlation and are excluded before graph construction, if any occur.

The correlation matrix is saved locally as `results/correlation_matrix.npy` and is excluded from Git.

## 6. Graph construction

The graph is undirected. A node represents a selected unit. An edge is added for a pair of units when `abs(r) >= 0.30`, where `r` is their Pearson correlation. The edge attributes are:

- `correlation`: signed Pearson correlation coefficient.
- `weight`: absolute Pearson correlation coefficient.

Because both positive and negative correlations can pass the threshold, network visualizations that use only `weight` conceal the sign unless `correlation` is inspected separately.

## 7. Network summary

The workflow computes node and edge counts, graph density, the number of connected components, and the size of the largest connected component using NetworkX.

Observed outputs for the current recording and parameter setting:

| Metric | Value |
|---|---:|
| Nodes | 113 |
| Edges | 1,621 |
| Density | 0.256163084703 |
| Connected components | 8 |
| Largest component | 106 nodes |

The graph is exported in GEXF and GraphML formats and the edge list is exported as CSV. Gephi is used for visualization. Visual cluster colors are not, by themselves, evidence of biological communities.

## 8. Reproduction

Use Python 3.14.0 and install the versions specified in `requirements.txt`. Place the authorized NWB file in `data/`, then run the scripts in the order shown in the repository README.

## 9. Dataset provenance

The inspected NWB file reports identifier `15a9c6eb-d2ac-4d49-ac7b-936c1fe3cb39` and session start `2020-01-16T15:53:21.500926-05:00`. The corresponding public archive identifier, authors, citation, version, and license have not yet been verified and must be added before the results are treated as a fully traceable research release.
