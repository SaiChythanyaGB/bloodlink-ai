# Architecture
Streamlit UI -> validation -> matching service -> deterministic compatibility and eligibility filters -> distance utility -> fuzzy inference -> GA and baselines -> SQLite persistence -> history and charts.

Compatibility is a hard constraint; neither fuzzy inference nor the GA can restore a filtered donor.
