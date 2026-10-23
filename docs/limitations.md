# Limitations and interpretation

## Correlation is not connectivity

An edge in this network indicates a Pearson correlation between two one-second spike-count series. It does **not** prove synaptic connectivity, information transfer, causal influence, or anatomical proximity. Common inputs, global activity fluctuations, behavior, and recording artifacts can induce correlations.

## Single-session scope

The reported network describes one NWB recording. It is not evidence of population-level reproducibility, cross-session stability, or generalization to other animals or experiments.

## Quality labels are inherited

The `good`/`mua` classification comes from the NWB source processing. This project does not independently review spike waveforms, refractory-period violations, drift, or unit stability.

## Temporal resolution and analysis duration

One-second spike-count bins discard millisecond-scale timing information. The analysis endpoint is derived from the last spike among selected units rather than a separately validated session end time. No lagged or time-resolved interaction model is fitted.

## Threshold sensitivity

The absolute-correlation threshold of 0.30 is exploratory. Edge count, density, connected components, and any visual community structure can change substantially with bin width, threshold, preprocessing, and recording segment.

## Statistical uncertainty

Pairwise correlations are not accompanied by confidence intervals, null models, permutation tests, multiple-comparison adjustments, or stability analyses. An edge therefore should not be interpreted as a statistically significant biological relationship.

## Signed relationships

The graph includes both positive and negative correlations when their absolute magnitude meets the threshold. The `weight` attribute stores magnitude only, while `correlation` preserves the sign. Analyses using only unsigned weights can mix qualitatively different relationships.

## Visualization is descriptive

Gephi layouts and colors are visual aids. Spatial proximity in a force-directed layout does not represent physical distance between neurons, and visual groupings are not validated cell types or neural circuits.

## Provenance and redistribution

The official source dataset, version, citation, and redistribution terms must be verified. Derived result files should be published only when the applicable data license and attribution requirements permit it.

## Suggested follow-up validation

Future work could test multiple bin widths and correlation thresholds, compare against spike-train surrogate/null models, inspect positive and negative subnetworks separately, control for behavioral covariates, assess stability across recording segments, and reproduce the workflow on additional sessions.
