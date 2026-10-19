from pathlib import Path
import sqlite3
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=ROOT/'data'; DB_PATH=DATA_DIR/'blood_bank.db'
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS donors(id INTEGER PRIMARY KEY AUTOINCREMENT, donor_code TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL, blood_group TEXT NOT NULL CHECK(blood_group IN ('O-','O+','A-','A+','B-','B+','AB-','AB+')), city_or_area TEXT NOT NULL DEFAULT '', latitude REAL, longitude REAL, availability_status TEXT NOT NULL DEFAULT 'Available' CHECK(availability_status IN ('Available','Unavailable')), last_donation_date TEXT, contact_preference TEXT NOT NULL DEFAULT 'Manual follow-up', eligibility_status TEXT NOT NULL DEFAULT 'Unknown' CHECK(eligibility_status IN ('Verified','Pending','Ineligible','Unknown')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS blood_requests(id INTEGER PRIMARY KEY AUTOINCREMENT, request_code TEXT NOT NULL UNIQUE, hospital_location TEXT NOT NULL, latitude REAL, longitude REAL, requested_blood_group TEXT NOT NULL CHECK(requested_blood_group IN ('O-','O+','A-','A+','B-','B+','AB-','AB+')), units_required INTEGER NOT NULL CHECK(units_required>0), urgency TEXT NOT NULL CHECK(urgency IN ('Low','Medium','High','Critical')), required_by TEXT NOT NULL, max_distance_km REAL, shortlist_size INTEGER NOT NULL DEFAULT 5 CHECK(shortlist_size>0), status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open','Matching in Progress','Partially Fulfilled','Fulfilled','Cancelled')), notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS matching_runs(id INTEGER PRIMARY KEY AUTOINCREMENT, request_id INTEGER NOT NULL REFERENCES blood_requests(id) ON DELETE CASCADE, algorithm_name TEXT NOT NULL, algorithm_config TEXT NOT NULL DEFAULT '{}', candidate_count INTEGER NOT NULL DEFAULT 0, execution_time_ms REAL NOT NULL DEFAULT 0, evaluation_metrics TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS matching_results(id INTEGER PRIMARY KEY AUTOINCREMENT, matching_run_id INTEGER NOT NULL REFERENCES matching_runs(id) ON DELETE CASCADE, donor_id INTEGER NOT NULL REFERENCES donors(id), rank INTEGER NOT NULL, fuzzy_score REAL NOT NULL, distance_km REAL, explanation TEXT NOT NULL DEFAULT '', fitness_contribution TEXT NOT NULL DEFAULT '{}', UNIQUE(matching_run_id,donor_id));
CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT, metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_donors_group ON donors(blood_group); CREATE INDEX IF NOT EXISTS idx_donors_avail ON donors(availability_status); CREATE INDEX IF NOT EXISTS idx_req_status ON blood_requests(status);
'''
@contextmanager
def connect():
    DATA_DIR.mkdir(parents=True,exist_ok=True); conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; conn.execute('PRAGMA foreign_keys=ON')
    try: yield conn; conn.commit()
    except Exception: conn.rollback(); raise
    finally: conn.close()
def init_db():
    with connect() as c:c.executescript(SCHEMA)
def log_action(conn,action,entity_type,entity_id=None,metadata='{}'):
    conn.execute('INSERT INTO audit_logs(action,entity_type,entity_id,metadata) VALUES(?,?,?,?)',(action,entity_type,str(entity_id) if entity_id is not None else None,metadata))
