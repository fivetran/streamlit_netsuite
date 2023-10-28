def extract_second_item(s):
    parts = [part.strip() for part in s.split(":")]
    return parts[1] if len(parts) > 1 else None