import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd
import plotly.express as px
import streamlit as st
from app.db import init_db,connect,log_action
from app.seed_data import seed_demo
from app.matching import run_matching
from app.algorithms.compatibility import BLOOD_GROUPS

st.set_page_config(page_title='BloodLink AI',page_icon='🩸',layout='wide')
init_db()

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}

/* Keep the sidebar consistently dark blue */
[data-testid="stSidebar"] {
    background-color: #102b3f;
}
[data-testid="stSidebar"] * {
    color: #f6f9fc;
}

/* Metric cards adapt to the selected Streamlit theme */
[data-testid="stMetric"] {
    background-color: var(--secondary-background-color);
    border: 1px solid var(--text-color);
    padding: 14px;
    border-radius: 12px;
}

/* Let Streamlit's theme control metric text color */
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: var(--text-color) !important;
}

/* Improve readability of form controls */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    color: var(--text-color);
}
</style>
""", unsafe_allow_html=True)
st.sidebar.title('🩸 BloodLink AI');

page=st.sidebar.radio('Navigation',['Overview','Donor Management','Emergency Requests','Donor Matching','Matching History','Algorithm Insights','Settings'])
st.title(page)
def dfq(q,p=()):
    with connect() as c:return pd.read_sql_query(q,c,params=p)

if page=='Overview':
    donors=dfq('SELECT * FROM donors');req=dfq('SELECT * FROM blood_requests');runs=dfq('SELECT * FROM matching_runs')
    a,b,c,d=st.columns(4);a.metric('Registered donors',len(donors));b.metric('Available donors',int((donors.availability_status=='Available').sum()) if len(donors) else 0);c.metric('Open requests',int(req.status.isin(['Open','Matching in Progress']).sum()) if len(req) else 0);d.metric('Matching runs',len(runs))
    x,y=st.columns(2)
    with x:
        st.subheader('Donors by blood group')
        if len(donors):st.plotly_chart(px.bar(donors.groupby('blood_group').size().reset_index(name='count'),x='blood_group',y='count'),use_container_width=True)
        else:st.info('No donor records yet. Load demo data in Settings.')
    with y:
        st.subheader('Requests by urgency')
        if len(req):st.plotly_chart(px.pie(req.groupby('urgency').size().reset_index(name='count'),names='urgency',values='count'),use_container_width=True)
        else:st.info('No requests yet.')
    st.subheader('Recent requests');st.dataframe(req.sort_values('created_at',ascending=False).head(10) if len(req) else req,use_container_width=True,hide_index=True)

elif page=='Donor Management':
    with st.form('add_donor',clear_on_submit=True):
        st.subheader('Register donor');a,b,c=st.columns(3);code=a.text_input('Donor code');name=b.text_input('Fictional display name');bg=c.selectbox('Blood group',BLOOD_GROUPS)
        a,b,c=st.columns(3);area=a.text_input('Area / city','Bengaluru');lat=b.number_input('Latitude',-90.,90.,12.9716,format='%.6f');lon=c.number_input('Longitude',-180.,180.,77.5946,format='%.6f')
        a,b,c=st.columns(3);avail=a.selectbox('Availability',['Available','Unavailable']);elig=b.selectbox('Eligibility',['Verified','Pending','Unknown','Ineligible']);pref=c.selectbox('Contact preference',['Manual follow-up','Phone follow-up','SMS preference'])
        submit=st.form_submit_button('Add donor',type='primary')
        if submit:
            if not code.strip() or not name.strip():st.error('Donor code and display name are required.')
            else:
                try:
                    with connect() as cn:
                        cur=cn.execute('INSERT INTO donors(donor_code,display_name,blood_group,city_or_area,latitude,longitude,availability_status,eligibility_status,contact_preference) VALUES(?,?,?,?,?,?,?,?,?)',(code.strip(),name.strip(),bg,area.strip(),lat,lon,avail,elig,pref));log_action(cn,'donor_created','donor',cur.lastrowid)
                    st.success('Donor added.');st.rerun()
                except Exception as e:st.error(f'Could not add donor: {e}')
    st.divider();donors=dfq('SELECT * FROM donors ORDER BY id DESC');search=st.text_input('Search donor code or name');a,b=st.columns(2);groups=a.multiselect('Blood group filter',list(BLOOD_GROUPS));statuses=b.multiselect('Availability filter',['Available','Unavailable'],default=['Available','Unavailable'])
    if search and len(donors):donors=donors[donors.donor_code.str.contains(search,case=False,na=False)|donors.display_name.str.contains(search,case=False,na=False)]
    if groups and len(donors):donors=donors[donors.blood_group.isin(groups)]
    if statuses and len(donors):donors=donors[donors.availability_status.isin(statuses)]
    st.dataframe(donors,use_container_width=True,hide_index=True);st.download_button('Export visible donors CSV',donors.to_csv(index=False).encode(),'donors.csv','text/csv')
    all_d=dfq('SELECT id,donor_code,display_name,availability_status,eligibility_status FROM donors ORDER BY donor_code')
    if len(all_d):
        st.subheader('Update donor status');labels={f'{r.donor_code} — {r.display_name} (ID {r.id})':int(r.id) for r in all_d.itertuples()};label=st.selectbox('Choose donor to update',list(labels));did=labels[label];cur=all_d[all_d.id==did].iloc[0]
        with st.form('update_donor'):
            av=st.selectbox('Availability status',['Available','Unavailable'],index=['Available','Unavailable'].index(cur.availability_status));el=st.selectbox('Eligibility status',['Verified','Pending','Unknown','Ineligible'],index=['Verified','Pending','Unknown','Ineligible'].index(cur.eligibility_status));save=st.form_submit_button('Save status')
            if save:
                with connect() as cn:cn.execute('UPDATE donors SET availability_status=?,eligibility_status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(av,el,did));log_action(cn,'donor_updated','donor',did)
                st.success('Donor updated.');st.rerun()
    st.caption('Eligibility is staff-entered operational information, not AI medical clearance. Sample names are fictional.')

elif page=='Emergency Requests':
    with st.form('add_request',clear_on_submit=True):
        st.subheader('Create blood request');a,b,c=st.columns(3);code=a.text_input('Request code');loc=b.text_input('Hospital / request location');bg=c.selectbox('Requested blood group',BLOOD_GROUPS)
        a,b,c=st.columns(3);units=a.number_input('Units required',1,100,2);urgency=b.selectbox('Urgency',['Low','Medium','High','Critical']);required=c.text_input('Required by (ISO date/time)','2026-12-31T12:00')
        a,b,c=st.columns(3);lat=a.number_input('Hospital latitude',-90.,90.,12.9716,format='%.6f');lon=b.number_input('Hospital longitude',-180.,180.,77.5946,format='%.6f');maxdist=c.number_input('Max distance km (0 = no limit)',0.,1000.,50.)
        shortlist=st.number_input('Target shortlist size',1,50,5);notes=st.text_area('Operational notes');submit=st.form_submit_button('Create request',type='primary')
        if submit:
            if not code.strip() or not loc.strip() or not required.strip():st.error('Request code, location, and required-by time are required.')
            else:
                try:
                    with connect() as cn:cn.execute('INSERT INTO blood_requests(request_code,hospital_location,latitude,longitude,requested_blood_group,units_required,urgency,required_by,max_distance_km,shortlist_size,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(code.strip(),loc.strip(),lat,lon,bg,int(units),urgency,required.strip(),maxdist if maxdist>0 else None,int(shortlist),notes.strip()));log_action(cn,'request_created','blood_request',code.strip())
                    st.success('Request created.');st.rerun()
                except Exception as e:st.error(f'Could not create request: {e}')
    st.divider();req=dfq('SELECT * FROM blood_requests ORDER BY created_at DESC');st.dataframe(req,use_container_width=True,hide_index=True)
    if len(req):
        st.subheader('Update request status');opts={f'{r.request_code} — {r.requested_blood_group} — {r.urgency}':int(r.id) for r in req.itertuples()};label=st.selectbox('Request',list(opts));status=st.selectbox('New status',['Open','Matching in Progress','Partially Fulfilled','Fulfilled','Cancelled'])
        if st.button('Save request status'):
            with connect() as cn:cn.execute('UPDATE blood_requests SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(status,opts[label]));log_action(cn,'request_status_changed','blood_request',opts[label],json.dumps({'status':status}))
            st.success('Status updated.');st.rerun()

elif page=='Donor Matching':
    req=dfq("SELECT * FROM blood_requests WHERE status!='Cancelled' ORDER BY created_at DESC")
    if req.empty:st.info('Create an emergency request first, or load demo data in Settings.')
    else:
        opts={f'{r.request_code} | {r.requested_blood_group} | {r.urgency} | {r.hospital_location}':int(r.id) for r in req.itertuples()};label=st.selectbox('Select request',list(opts));strict=st.checkbox('Strict eligibility: only Verified donors',True);available=st.checkbox('Require Available donors',True);seed=st.number_input('GA random seed',0,999999,7)
        if st.button('Run matching',type='primary'):
            try:st.session_state['last_match']=run_matching(opts[label],strict,available,int(seed));st.success(f"Matching run #{st.session_state['last_match']['run_id']} saved.")
            except Exception as e:st.error(f'Matching failed: {e}')
        result=st.session_state.get('last_match')
        if result and result['request']['id']==opts[label]:
            st.subheader('Filter counts');counts=result['counts'];cols=st.columns(5)
            for col,key,title in zip(cols,['total','incompatible','eligibility','availability','distance'],['All donors','Incompatible','Eligibility excluded','Availability excluded','Distance excluded']):col.metric(title,counts[key])
            st.subheader('GA-optimized shortlist');selected=result['methods']['GA-optimized']
            if selected:
                view=pd.DataFrame(selected)
                columns=[c for c in ['rank','donor_code','display_name','blood_group','city_or_area','distance_km','availability_status','eligibility_status','fuzzy_score','explanation'] if c in view.columns]
                st.dataframe(view[columns],use_container_width=True,hide_index=True)
            else:st.warning('No candidates passed the configured hard filters. No constraints were relaxed.')
            st.subheader('Baseline comparison');rows=[{'Method':n,**m,'GA fitness':result['ga_fitness'] if n=='GA-optimized' else None} for n,m in result['metrics'].items()];md=pd.DataFrame(rows);st.dataframe(md,use_container_width=True,hide_index=True)
            melted=md[['Method','mean_fuzzy_score','availability_rate']].melt('Method',var_name='Metric',value_name='Value');st.plotly_chart(px.bar(melted,x='Method',y='Value',color='Metric',barmode='group'),use_container_width=True)
            st.caption(f"Runtime: {result['runtime_ms']:.2f} ms. Operational demo only; no clinical superiority is claimed.")


elif page == 'Matching History':
    runs = dfq(
        'SELECT mr.id run_id, br.request_code, br.requested_blood_group, '
        'br.urgency, mr.algorithm_name, mr.candidate_count, '
        'mr.execution_time_ms, mr.created_at, mr.evaluation_metrics '
        'FROM matching_runs mr '
        'JOIN blood_requests br ON br.id = mr.request_id '
        'ORDER BY mr.created_at DESC'
    )

    st.dataframe(
        runs.drop(columns=['evaluation_metrics']) if len(runs) else runs,
        use_container_width=True,
        hide_index=True
    )

    if len(runs):
        rid = runs.run_id.iloc[0]

        details = dfq(
            'SELECT res.rank, d.donor_code, d.display_name, d.blood_group, '
            'res.fuzzy_score, res.distance_km, res.explanation '
            'FROM matching_results res '
            'JOIN donors d ON d.id = res.donor_id '
            'WHERE res.matching_run_id = ? ORDER BY res.rank',
            (int(rid),)
        )

        st.subheader("Selected donor details")
        st.dataframe(
            details,
            use_container_width=True,
            hide_index=True
        )

        '''with st.expander("View algorithm comparison metrics"):
            st.json(
                json.loads(
                    runs[runs.run_id == rid].iloc[0].evaluation_metrics
                )
            )'''
    else:
        st.info("No matching history yet. Run donor matching first.")

elif page=='Algorithm Insights':
    st.markdown('''### Architecture
Emergency request + donor database → deterministic compatibility filter → eligibility / availability / distance constraints → fuzzy priority scoring → Genetic Algorithm → ranked shortlist → SQLite history.

### Fuzzy Logic
Urgency, distance, and availability are mapped to overlapping triangular membership functions. Rules use minimum firing strength; output sets use maximum aggregation; centroid defuzzification returns a score from 0 to 100. Missing distance is conservatively treated as far for scoring and fails a configured maximum-distance constraint.

### Genetic Algorithm
A chromosome is an ordered shortlist of unique donor IDs. The GA uses seeded initialization, tournament selection, order-preserving crossover, swap mutation, elitism, and a rank-weighted fitness objective. Donor utility is 65% fuzzy score, 25% availability, and 10% distance quality.

### Baselines
Nearest-compatible, availability-first, and fuzzy-score-first are evaluated against the same filtered candidate pool and shortlist size. Outcomes are computed from the current data; the GA is not guaranteed to outperform each baseline.

### Limitations
This is not a clinically validated system. The ABO/Rh compatibility table is simplified; real transfusion requires component-specific protocols, antibody screening, crossmatching, and authorized clinical review. Eligibility is manually entered. Distances are straight-line estimates. Synthetic data cannot validate real-world effectiveness.''')
    st.code('Urgency: Low (0,0,4), Medium (2,5,8), High (6,10,10)\nDistance: Near (0,0,20), Moderate (10,35,60), Far (45,100,100)\nAvailability: Low (0,0,4), Medium (2,5,8), High (6,10,10)\nOutput: Very Low (0,0,25), Low (10,25,45), Medium (30,50,70), High (55,75,90), Very High (80,100,100)')

elif page=='Settings':
    with connect() as cn:st.write(f"Local SQLite database: `{Path(__file__).resolve().parent/'data'/'blood_bank.db'}`");st.write(f"Donors: {cn.execute('SELECT COUNT(*) FROM donors').fetchone()[0]} · Requests: {cn.execute('SELECT COUNT(*) FROM blood_requests').fetchone()[0]}")
    if st.button('Load demo data if database is empty'):
        res=seed_demo(False);st.success(f"Donors: {res['donors']}; requests: {res['requests']}; existing data preserved: {res['skipped']}")
    with st.expander('Danger zone: reset and reload sample data'):
        confirm=st.checkbox('I understand this deletes local donors, requests, and matching history.')
        if st.button('Reset and reload demo data',disabled=not confirm):res=seed_demo(True);st.success(f"Loaded {res['donors']} fictional donors and {res['requests']} requests.");st.rerun()
    for table in ['donors','blood_requests','matching_runs','matching_results','audit_logs']:
        export=dfq(f'SELECT * FROM {table}');st.download_button(f'Export {table}.csv',export.to_csv(index=False).encode(),f'{table}.csv','text/csv',key=f'export_{table}')
    st.warning('Local demo has no authentication. Do not enter real donor or patient information.')
