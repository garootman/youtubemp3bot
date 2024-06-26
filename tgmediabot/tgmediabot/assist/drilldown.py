def drilldown(obj, drillist):
    if not obj or not drillist:
        return obj
    for key in drillist:
        try:
            obj = obj[key]
        except (KeyError, IndexError, TypeError):
            return None
    return obj
