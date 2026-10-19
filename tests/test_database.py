import app.db as db
def test_schema_initializes(monkeypatch,tmp_path):
    monkeypatch.setattr(db,'DATA_DIR',tmp_path);monkeypatch.setattr(db,'DB_PATH',tmp_path/'test.db');db.init_db()
    with db.connect() as c:tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {'donors','blood_requests','matching_runs','matching_results','audit_logs'}<=tables
