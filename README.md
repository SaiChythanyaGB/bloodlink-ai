# AI-Based Blood Donor Matching & Emergency Prioritization System

Runnable academic prototype using Python, Streamlit, SQLite, Mamdani-style fuzzy inference, and a Genetic Algorithm.

## Features
- Dashboard and charts from stored data
- Donor management and status updates
- Emergency request creation and status tracking
- Simplified deterministic donor-to-recipient ABO/Rh compatibility filtering
- Eligibility and availability gates
- Haversine distance calculations
- Fuzzy priority scores from urgency, distance, and availability
- Genuine seeded GA with selection, crossover, mutation, elitism, and fitness evaluation
- Baseline comparisons and persisted matching history
- 100 fictional demo donors, 3 fictional requests, CSV exports, tests

## Run on Windows PowerShell
```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.seed_data
streamlit run app.py
```

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed_data
streamlit run app.py
```

## Test
```bash
pytest -q
```

The local database is created at `data/blood_bank.db`. Use Settings to load demo data or reset the fictional sample dataset. Do not use real donor or patient information.

## Algorithm overview
1. Hard filter incompatible donors.
2. Apply eligibility, availability, and optional maximum-distance rules.
3. Calculate operational fuzzy score from urgency, distance, and availability using overlapping triangular membership functions, min rule firing, max aggregation, and centroid defuzzification.
4. Run a seeded GA on the remaining candidate pool. The weighted donor utility is 65% fuzzy score, 25% availability, and 10% distance quality; rank-weighted fitness favors better candidates earlier in the shortlist.
5. Compare against nearest-first, availability-first, and fuzzy-score-first baselines using the same candidate pool.

## Important limitations
This is not clinically validated and must not guide actual transfusions. Compatibility is a simplified red blood cell ABO/Rh educational model. Actual transfusion decisions require component-specific rules, antibody screening, crossmatching, and authorized clinical review. Eligibility is staff-entered, not medically inferred. Distance is straight-line distance, not travel time. Synthetic data cannot establish real-world effectiveness. Local SQLite and no authentication are not production-ready.
