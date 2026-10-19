import pytest
from app.algorithms.fuzzy_priority import fuzzy_priority
def test_bounds():
    for u in ['Low','Medium','High','Critical']:
        for a in ['Available','Unavailable','Unknown']:assert 0<=fuzzy_priority(u,20,a)<=100
def test_urgent_near_available_scores_higher():assert fuzzy_priority('Critical',2,'Available')>fuzzy_priority('Low',90,'Available')
def test_missing_distance_conservative():assert fuzzy_priority('High',None,'Available')<fuzzy_priority('High',2,'Available')
def test_invalid_urgency():
    with pytest.raises(ValueError):fuzzy_priority('Extreme',5,'Available')
