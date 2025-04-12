import uuid
def generate_uuid() -> str:
    """Generate a new UUID as a string."""
    return str(uuid.uuid4())