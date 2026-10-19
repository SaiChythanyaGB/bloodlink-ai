# Algorithm notes

## Compatibility
Explicit donor-to-recipient lookup table for a simplified red blood cell ABO/Rh educational model.

## Distance
Haversine great-circle distance using mean Earth radius 6371.0088 km.

## Fuzzy inference
Triangular membership functions are defined in `app/algorithms/fuzzy_priority.py`. Rule firing uses min for conjunction, max for output aggregation, and centroid defuzzification over integer scores 0–100. Missing distance is treated conservatively as far for scoring; if a maximum distance is configured, missing distance fails that hard filter.

## Genetic Algorithm
Chromosomes are ordered unique candidate ID lists. Donor utility = 0.65 * normalized fuzzy score + 0.25 * availability indicator + 0.10 * distance quality. Distance quality is `1 - min(distance_km,100)/100`, or zero when unavailable. Fitness is a rank-weighted average. Tournament selection, order-preserving crossover, swap mutation, elitism, and a seeded random generator are used.
