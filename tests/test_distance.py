import pytest
from app.algorithms.distance import haversine_km
def test_same_point():assert haversine_km(12,77,12,77)==pytest.approx(0)
def test_city_distance():assert 280<haversine_km(12.9716,77.5946,13.0827,80.2707)<310
def test_missing():assert haversine_km(None,1,2,3) is None
def test_bad_lat():
    with pytest.raises(ValueError):haversine_km(91,0,0,0)
