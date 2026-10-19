import math

def haversine_km(lat1, lon1, lat2, lon2):
    if any(v is None for v in (lat1, lon1, lat2, lon2)):
        return None
    try: lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError): return None
    if not (-90 <= lat1 <= 90 and -90 <= lat2 <= 90): raise ValueError("Latitude must be between -90 and 90.")
    if not (-180 <= lon1 <= 180 and -180 <= lon2 <= 180): raise ValueError("Longitude must be between -180 and 180.")
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371.0088 * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0, 1-a)))
