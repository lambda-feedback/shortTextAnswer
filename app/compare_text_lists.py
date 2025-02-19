def process_list(input_list):
    """
    Detects if the input is a list, and if any element in the list contains semicolons,
    it splits that element into multiple elements.

    Args:
        input_list (list): A list of strings.

    Returns:
        list: A processed list where semicolon-separated elements are split into separate elements.
    """
    if not isinstance(input_list, list):
        raise ValueError("Input must be a list of strings.")

    processed_list = []
    for item in input_list:
        if not isinstance(item, str):
            raise ValueError("All elements in the input list must be strings.")

        # Split by semicolon if present, otherwise keep the original item
        processed_list.extend(item.split(';') if ';' in item else [item])

    return processed_list
def test_process_list():
    """
    Unit tests for process_list function.
    """
    test_cases = [
        (["apple", "banana;orange", "grape"], ["apple", "banana", "orange", "grape"]),
        (["one;two;three", "four", "five"], ["one", "two", "three", "four", "five"]),
        (["alpha;beta", "gamma;delta;epsilon"], ["alpha", "beta", "gamma", "delta", "epsilon"]),
        (["no_separator"], ["no_separator"]),
        ([], []),
        (["single"], ["single"]),
    ]

    for i, (input_list, expected_output) in enumerate(test_cases):
        assert process_list(input_list) == expected_output, f"Test case {i+1} failed"

    print("All test cases passed!")

# Run the tests
test_process_list()
