def rank_baseline(donors, method, shortlist_size=5):
    if method=="Nearest-compatible": key=lambda d:(d.get("distance_km") is None,d.get("distance_km") if d.get("distance_km") is not None else float("inf"))
    elif method=="Availability-first": key=lambda d:(d.get("availability_status")!="Available",-float(d.get("fuzzy_score",0)))
    elif method=="Fuzzy-score-first": key=lambda d:-float(d.get("fuzzy_score",0))
    else: raise ValueError("Unknown baseline method")
    return [dict(d,rank=i+1) for i,d in enumerate(sorted(donors,key=key)[:max(0,shortlist_size)])]

def evaluate_selection(selected):
    if not selected:return {"selected_count":0,"mean_fuzzy_score":0.0,"availability_rate":0.0,"mean_distance_km":None}
    distances=[float(d['distance_km']) for d in selected if d.get('distance_km') is not None]
    return {"selected_count":len(selected),"mean_fuzzy_score":sum(float(d.get('fuzzy_score',0)) for d in selected)/len(selected),"availability_rate":sum(d.get('availability_status')=="Available" for d in selected)/len(selected),"mean_distance_km":sum(distances)/len(distances) if distances else None}
