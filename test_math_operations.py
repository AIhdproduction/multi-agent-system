import pytest
from math_operations import multiply

# Unit Tests

def test_multiply_happy_path():
    assert multiply(5, 4) == 20
    assert multiply(-2, 3) == -6
    assert multiply(0, 10) == 0
    assert multiply(2.5, 4) == 10.0
    assert multiply(-1.5, -2) == 3.0

def test_multiply_edge_cases():
    assert multiply(1, 1) == 1
    assert multiply(0, 0) == 0
    assert multiply(1000000, 1000000) == 1000000000000
    assert multiply(-1, 1) == -1
    assert multiply(1, -1) == -1

def test_multiply_error_handling():
    with pytest.raises(TypeError):
        multiply('a', 5)
    with pytest.raises(TypeError):
        multiply(5, 'b')
    with pytest.raises(TypeError):
        multiply(None, 5)
    with pytest.raises(TypeError):
        multiply(5, None)
    with pytest.raises(TypeError):
        multiply([1, 2], 3)
    with pytest.raises(TypeError):
        multiply(3, [1, 2])

# Integration Tests (simple example as there's only one function)
def test_multiply_integration_with_other_operations():
    # This is a very basic integration test. In a real scenario, this would involve 
    # multiple functions or modules interacting.
    result1 = multiply(6, 7)
    result2 = multiply(result1, 2) # Multiply the result of the first multiplication
    assert result2 == 84 
    
    # Example using a variable that might come from another part of the system
    input_a = 10
    input_b = 0.5
    intermediate_result = multiply(input_a, input_b)
    assert intermediate_result == 5.0

# Further Edge Cases and Error Handling considered:
# - Very large numbers: Handled in test_multiply_edge_cases (e.g., 1000000 * 1000000)
# - Negative numbers: Handled in test_multiply_happy_path and test_multiply_edge_cases
# - Special characters: Implicitly handled by TypeError in test_multiply_error_handling
# - Concurrent Access: Not applicable for a simple procedural function like this.
#   Concurrency testing would be relevant for shared resources, stateful objects, or database interactions.

# Performance: For a simple multiplication, performance is generally not a concern.
# If this were a complex mathematical operation on very large datasets, 
# performance tests (e.g., using pytest-benchmark) would be necessary.
