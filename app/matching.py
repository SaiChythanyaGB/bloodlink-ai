import json,time
from .db import connect,log_action
from .algorithms.compatibility import is_compatible
from .algorithms.distance import haversine_km
from .algorithms.fuzzy_priority import fuzzy_priority
from .algorithms.genetic_optimizer import optimize
from .algorithms.baselines import rank_baseline,evaluate_selection

def run_matching(request_id,strict_eligibility=True,require_available=True,seed=7):
    start=time.perf_counter()
    with connect() as c:
        req=c.execute('SELECT * FROM blood_requests WHERE id=?',(request_id,)).fetchone()
        if not req:raise ValueError('Request not found')
        donors=[dict(r) for r in c.execute('SELECT * FROM donors').fetchall()]
        counts={'total':len(donors),'incompatible':0,'eligibility':0,'availability':0,'distance':0}; candidates=[]
        for d in donors:
            if not is_compatible(d['blood_group'],req['requested_blood_group']):counts['incompatible']+=1;continue
            if d['eligibility_status']=='Ineligible' or (strict_eligibility and d['eligibility_status']!='Verified'):counts['eligibility']+=1;continue
            if require_available and d['availability_status']!='Available':counts['availability']+=1;continue
            dist=haversine_km(req['latitude'],req['longitude'],d['latitude'],d['longitude'])
            if req['max_distance_km'] is not None and (dist is None or dist>req['max_distance_km']):counts['distance']+=1;continue
            d['distance_km']=dist; d['fuzzy_score']=fuzzy_priority(req['urgency'],dist,d['availability_status'],req['max_distance_km'] or 100.0)
            d['explanation']=f"Urgency={req['urgency']}; distance={dist:.1f} km" if dist is not None else f"Urgency={req['urgency']}; distance unavailable (treated conservatively as far)"
            d['explanation']+=f"; availability={d['availability_status']}; fuzzy priority={d['fuzzy_score']:.1f}/100."
            candidates.append(d)
        k=min(req['shortlist_size'],len(candidates)); ga=optimize(candidates,k,seed=seed)
        methods={'GA-optimized':ga['selected'],'Nearest-compatible':rank_baseline(candidates,'Nearest-compatible',k),'Availability-first':rank_baseline(candidates,'Availability-first',k),'Fuzzy-score-first':rank_baseline(candidates,'Fuzzy-score-first',k)}
        metrics={name:evaluate_selection(sel) for name,sel in methods.items()}; elapsed=(time.perf_counter()-start)*1000
        cur=c.execute('INSERT INTO matching_runs(request_id,algorithm_name,algorithm_config,candidate_count,execution_time_ms,evaluation_metrics) VALUES(?,?,?,?,?,?)',(request_id,'Fuzzy Logic + Genetic Algorithm',json.dumps({'seed':seed,'strict_eligibility':strict_eligibility,'require_available':require_available}),len(candidates),elapsed,json.dumps(metrics)))
        run_id=cur.lastrowid
        for rank,d in enumerate(ga['selected'],1):c.execute('INSERT INTO matching_results(matching_run_id,donor_id,rank,fuzzy_score,distance_km,explanation,fitness_contribution) VALUES(?,?,?,?,?,?,?)',(run_id,d['id'],rank,d['fuzzy_score'],d['distance_km'],d['explanation'],json.dumps({'utility':d.get('ga_utility',0)})))
        log_action(c,'matching_run_created','matching_run',run_id,json.dumps({'request_id':request_id,'candidate_count':len(candidates)}))
        return {'run_id':run_id,'request':dict(req),'counts':counts,'candidates':candidates,'methods':methods,'metrics':metrics,'ga_fitness':ga['fitness'],'runtime_ms':elapsed}
