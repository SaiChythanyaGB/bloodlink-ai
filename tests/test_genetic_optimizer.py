from app.algorithms.genetic_optimizer import optimize,fitness
def ds():return [{'id':1,'fuzzy_score':95,'availability_status':'Available','distance_km':2},{'id':2,'fuzzy_score':40,'availability_status':'Unavailable','distance_km':30},{'id':3,'fuzzy_score':80,'availability_status':'Available','distance_km':8},{'id':4,'fuzzy_score':70,'availability_status':'Available','distance_km':15}]
def test_empty():assert optimize([],3)['selected']==[]
def test_unique_and_known():
    ids=[d['id'] for d in optimize(ds(),3,seed=21)['selected']];assert len(ids)==len(set(ids))==3;assert set(ids)<={1,2,3,4}
def test_seed_reproducibility():
    a=optimize(ds(),3,seed=44);b=optimize(ds(),3,seed=44);assert [x['id'] for x in a['selected']]==[x['id'] for x in b['selected']];assert a['fitness']==b['fitness']
def test_one_candidate():assert len(optimize([ds()[0]],5)['selected'])==1
def test_duplicate_fitness_invalid():assert fitness(['1','1'],{'1':ds()[0]})<0
