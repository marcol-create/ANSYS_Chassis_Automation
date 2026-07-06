raise RuntimeError(str([a for a in dir(seat_sm)
    if 'guide' in a.lower() or 'xtrus' in a.lower()]))
