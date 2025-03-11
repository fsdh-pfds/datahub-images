# test_function_app.py
from function_app import keys_upper

def test_keys_upper_simple():
    input_data = {'a': 'value', 'b': 123}
    expected = {'A': 'value', 'B': 123}
    result = keys_upper(input_data)
    assert result == expected

def test_keys_upper_nested():
    input_data = {
        'a': 'value',
        'b': {'inner': 'test'},
        'c': [{'d': 'nested'}]
    }
    expected = {
        'A': 'value',
        'B': {'Inner': 'test'},
        'C': [{'D': 'nested'}]
    }
    result = keys_upper(input_data)
    assert result == expected
