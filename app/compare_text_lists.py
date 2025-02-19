def parse_input(input_data):
    """
    Parses input data, handling both semicolon-separated strings and nested list structures.
    
    Args:
        input_data (str or list): A semicolon-separated string or a nested list.
    
    Returns:
        list: A processed list of elements.
    """
    if isinstance(input_data, str):
        if input_data == "":
            return []
        return [item for item in input_data.split(';') if item]
    elif isinstance(input_data, list) and all(isinstance(sublist, list) for sublist in input_data):
        return [item for sublist in input_data for item in sublist]
    else:
        raise ValueError("Input must be either a semicolon-separated string or a nested list.")

# Testing Code
def test_parse_input():
    test_cases = [
        ("apple;banana;cherry", ["apple", "banana", "cherry"]),
        ("one;two;three;four", ["one", "two", "three", "four"]),
        ("hello", ["hello"]),
        ("a;b;c;d;e", ["a", "b", "c", "d", "e"]),
        ("", []),  # Edge case: empty string to empty list
        ("word1;;word2", ["word1", "word2"]),  # Edge case: consecutive semicolons ignored
        ([["a"], ["b"], ["c"], ["d"]], ["a", "b", "c", "d"]),
        ([["apple"], ["banana"], ["cherry"]], ["apple", "banana", "cherry"]),
        ([[]], []),  # Edge case: list of empty lists
    ]
    
    for i, (input_data, expected) in enumerate(test_cases, 1):
        result = parse_input(input_data)
        assert result == expected, f"Test case {i} failed: {result} != {expected}"
    
    print("All test cases passed!")

# Run tests
test_parse_input()
