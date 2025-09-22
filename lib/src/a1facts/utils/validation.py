from datetime import datetime

def check_type(value: str, expected_type: str) -> bool:
    """Validates if a string value can be cast to the expected type."""
    if expected_type == 'str':
        return True
    if expected_type == 'float':
        try:
            float(value)
            return True
        except ValueError:
            return False
    if expected_type == 'int':
        try:
            int(value)
            return True
        except ValueError:
            return False
    if expected_type == 'bool':
        return value.lower() in ['true', 'false']
    if expected_type == 'date':
        try:
            # Matches YYYY-MM-DD format
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False
    return False
