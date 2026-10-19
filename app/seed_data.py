import random
from datetime import date,timedelta
from .db import init_db,connect,log_action
from .algorithms.compatibility import BLOOD_GROUPS
AREAS=[('Central',12.9716,77.5946),('North',13.0358,77.5970),('South',12.9141,77.5990),('East',12.9850,77.6500),('West',12.9750,77.5300),('Whitefield',12.9698,77.7500),('Yelahanka',13.1007,77.5963),('Electronic City',12.8399,77.6770)]
NAMES=['Alex Demo','Jordan Sample','Taylor Fiction','Morgan Test','Casey Example','Riley Mock','Avery Sample','Cameron Demo','Drew Example','Quinn Fiction']
def seed_demo(force=False):
    init_db(); rng=random.Random(2026)
    with connect() as c:
        count=c.execute('SELECT COUNT(*) FROM donors').fetchone()[0]
        if count and not force:return {'donors':count,'requests':c.execute('SELECT COUNT(*) FROM blood_requests').fetchone()[0],'skipped':True}
        if force:
            for table in ('matching_results','matching_runs','blood_requests','donors','audit_logs'):c.execute(f'DELETE FROM {table}')
        for i in range(100):
            area,lat,lon=rng.choice(AREAS)
            c.execute('''INSERT INTO donors(donor_code,display_name,blood_group,city_or_area,latitude,longitude,availability_status,last_donation_date,contact_preference,eligibility_status) VALUES(?,?,?,?,?,?,?,?,?,?)''',
            (f'D{i+1:04d}',f'{rng.choice(NAMES)} {i+1:03d}',rng.choice(BLOOD_GROUPS),area,lat+rng.uniform(-.012,.012),lon+rng.uniform(-.012,.012),rng.choices(['Available','Unavailable'],[.72,.28])[0],(date.today()-timedelta(days=rng.randint(90,700))).isoformat(),rng.choice(['Phone follow-up','SMS preference','Manual follow-up']),rng.choices(['Verified','Pending','Unknown','Ineligible'],[.70,.14,.10,.06])[0]))
        requests=[('REQ-1001','Central Hospital Demo',12.9716,77.5946,'O-',3,'Critical',(date.today()+timedelta(days=1)).isoformat()+'T09:00',50,5,'Fictional demonstration request.'),('REQ-1002','East Clinic Demo',12.985,77.65,'A+',2,'High',(date.today()+timedelta(days=2)).isoformat()+'T12:00',35,5,'Synthetic data only.'),('REQ-1003','South Hospital Demo',12.9141,77.599,'B+',4,'Medium',(date.today()+timedelta(days=3)).isoformat()+'T16:00',None,6,'Synthetic data only.')]
        for row in requests:c.execute('''INSERT INTO blood_requests(request_code,hospital_location,latitude,longitude,requested_blood_group,units_required,urgency,required_by,max_distance_km,shortlist_size,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',row)
        log_action(c,'demo_data_seeded','database',None,'{"fictional":true}')
    return {'donors':100,'requests':3,'skipped':False}
if __name__=='__main__':print(seed_demo())
