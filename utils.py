def validate_time(map_name: str, time_mins: int, time_s: int,
    time_ms: int, tracks: list[str]) -> bool:
    if map_name not in tracks:
        return False
    if time_mins < 0 or time_mins >= 60:
        return False
    if time_s < 0 or time_s >= 60:
        return False
    if time_ms < 0 or time_ms >= 1000:
        return False
    return True
