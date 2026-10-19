"""Genetic Algorithm for operational shortlist ordering, not clinical decisions."""
import random, time

def donor_utility(d):
    score=float(d.get("fuzzy_score",0))/100
    available=1.0 if d.get("availability_status")=="Available" else 0.0
    dist=d.get("distance_km")
    near=1-min(float(dist),100)/100 if dist is not None else 0.0
    return .65*score+.25*available+.10*near

def fitness(chromosome, by_id):
    if not chromosome or len(set(chromosome)) != len(chromosome) or any(x not in by_id for x in chromosome): return -1.0
    n=len(chromosome); return sum(donor_utility(by_id[x])*(n-i) for i,x in enumerate(chromosome))/sum(range(1,n+1))

def _ox(p1,p2,rng):
    n=len(p1)
    if n<2:return p1[:]
    a,b=sorted(rng.sample(range(n),2)); child=[None]*n; child[a:b+1]=p1[a:b+1]
    rest=[x for x in p2 if x not in child]; it=iter(rest)
    for i,x in enumerate(child):
        if x is None: child[i]=next(it)
    return child

def optimize(donors, shortlist_size=5, population_size=40, generations=50, crossover_probability=.85, mutation_probability=.2, seed=7):
    start=time.perf_counter()
    by_id={str(d['id']):d for d in donors}
    ids=list(by_id)
    if not ids:return {"selected":[],"fitness":0.0,"runtime_ms":(time.perf_counter()-start)*1000,"generations":0}
    k=min(max(1,int(shortlist_size)),len(ids)); rng=random.Random(seed); n=max(6,int(population_size))
    heuristic=sorted(ids,key=lambda x:donor_utility(by_id[x]),reverse=True)[:k]
    pop=[heuristic]+[rng.sample(ids,k) for _ in range(n-1)]
    score=lambda ch:fitness(ch,by_id)
    best=max(pop,key=score)[:]; bestscore=score(best); done=0
    for gen in range(max(1,int(generations))):
        done=gen+1; ranked=sorted(pop,key=score,reverse=True)
        if score(ranked[0])>bestscore: best,bestscore=ranked[0][:],score(ranked[0])
        nxt=[ranked[0][:],ranked[1][:]]
        while len(nxt)<n:
            pool=ranked[:min(10,len(ranked))]
            p1=max(rng.sample(pool,min(3,len(pool))),key=score)
            p2=max(rng.sample(pool,min(3,len(pool))),key=score)
            child=_ox(p1,p2,rng) if rng.random()<crossover_probability else p1[:]
            if len(child)>1 and rng.random()<mutation_probability:
                i,j=rng.sample(range(len(child)),2); child[i],child[j]=child[j],child[i]
            nxt.append(child)
        pop=nxt
    final=max([best]+pop,key=score)
    selected=[dict(by_id[x],rank=i+1,ga_utility=donor_utility(by_id[x])) for i,x in enumerate(final)]
    return {"selected":selected,"fitness":float(score(final)),"runtime_ms":(time.perf_counter()-start)*1000,"generations":done}
