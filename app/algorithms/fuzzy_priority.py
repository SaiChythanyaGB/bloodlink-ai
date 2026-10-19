"""Mamdani-style fuzzy inference with triangular membership functions and centroid defuzzification."""
import numpy as np

def trimf(x, abc):
    a,b,c = map(float, abc); x=np.asarray(x,dtype=float); y=np.zeros_like(x)
    if b>a:
        m=(x>=a)&(x<=b); y[m]=(x[m]-a)/(b-a)
    if c>b:
        m=(x>=b)&(x<=c); y[m]=np.maximum(y[m],(c-x[m])/(c-b))
    y[x==b]=1.0
    return np.clip(y,0,1)

URGENCY={"Low":(0,0,4),"Medium":(2,5,8),"High":(6,10,10)}
DISTANCE={"Near":(0,0,20),"Moderate":(10,35,60),"Far":(45,100,100)}
AVAILABILITY={"Low":(0,0,4),"Medium":(2,5,8),"High":(6,10,10)}
OUTPUT={"Very Low":(0,0,25),"Low":(10,25,45),"Medium":(30,50,70),"High":(55,75,90),"Very High":(80,100,100)}

def _membership(value, sets): return {k:float(trimf(np.array([value]),v)[0]) for k,v in sets.items()}
def fuzzy_priority(urgency, distance_km, availability, max_distance_km=None):
    if urgency not in ("Low","Medium","High","Critical"): raise ValueError("Unknown urgency.")
    if availability not in ("Available","Unavailable","Unknown"): raise ValueError("Unknown availability.")
    uval={"Low":2.,"Medium":5.,"High":9.,"Critical":10.}[urgency]
    aval={"Available":9.,"Unavailable":1.,"Unknown":3.}[availability]
    dist=100. if distance_km is None else min(100.,max(0.,float(distance_km)))
    if max_distance_km and max_distance_km>0: dist=min(100.,dist*100./max_distance_km)
    u,d,a=_membership(uval,URGENCY),_membership(dist,DISTANCE),_membership(aval,AVAILABILITY)
    ul={"Low":0,"Medium":1,"High":2}; out_names=["Very Low","Low","Medium","High","Very High"]
    universe=np.arange(101,dtype=float); aggregate=np.zeros_like(universe)
    for un,um in u.items():
      for dn,dm in d.items():
       for an,am in a.items():
        # Urgency, availability, and proximity combine to set the consequent level.
        level=2+(ul[un]-1)+(1 if an=="High" else -1 if an=="Low" else 0)+(1 if dn=="Near" else -1 if dn=="Far" else 0)
        label=out_names[max(0,min(4,level))]; strength=min(um,dm,am)
        if strength>0: aggregate=np.maximum(aggregate,np.minimum(strength,trimf(universe,OUTPUT[label])))
    area=float(aggregate.sum())
    return float(np.dot(universe,aggregate)/area) if area>1e-9 else 0.0
