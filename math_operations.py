def multiply(a, b):
    """Multiplies two numbers and returns the result."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers.")
    return a * b