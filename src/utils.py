"""random functions that are used more than once"""

def combine_dicts(d1, d2):
    #TODO
    #accept any number of input dicts
    out = {}
    for key in set(list(d1.keys()) + list(d2.keys())):
        if key in d1 and not key in d2:
            out[key] = d1[key]
            
        elif key in d2 and key not in d1:
            out[key] = d2[key]
            
        else:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                out[key] = combine_dicts(d1[key], d2[key])

            else:
                print(d1[key], d2[key])
                out[key] = d1[key] + d2[key]
                
    return out

def iter2str(t):
    """converts tuple to str and cuts off ()"""
    return str(t)[1:-1]