# tdd.py
def split_message(text: str, max_length: int) -> list[str]:
    """
    Splits a given text into a list of strings, ensuring no string exceeds
    the max_length. The splitting prioritizes newlines, but will forcefully
    split lines that are too long.

    Args:
        text: The input string to be split.
        max_length: The maximum allowed length for any string in the output list.

    Returns:
        A list of strings, representing the split parts of the original text.
    """
    # ========================================================================
    # STEP 2: IMPLEMENTATION to pass the tests
    # ========================================================================

    # Handle the edge case of an empty input string.
    if not text:
        return []

    # First, split the entire text into lines based on the newline character.
    # This respects the primary splitting rule.
    lines = text.splitlines()

    message_parts = []
    current_part = ""

    for line in lines:
        # CASE 1: The line itself is longer than max_length and must be force-split.
        if len(line) > max_length:
            # First, if there's a pending part from previous lines, add it to our list.
            if current_part:
                message_parts.append(current_part)
                current_part = ""
            
            # Force-split the oversized line into chunks of max_length.
            for i in range(0, len(line), max_length):
                message_parts.append(line[i:i + max_length])
            continue

        # CASE 2: The line is not too long, so we try to group it with the current part.
        
        # Determine the length if we add the new line.
        # If current_part is not empty, we need to add a newline character back in.
        potential_length = len(current_part) + len(line) + (1 if current_part else 0)

        if potential_length <= max_length:
            # If it fits, append the line to the current part.
            if not current_part:
                current_part = line
            else:
                current_part += "\n" + line
        else:
            # If it doesn't fit, the current part is complete. Add it to the list.
            message_parts.append(current_part)
            # The current line becomes the start of the new part.
            current_part = line

    # After the loop, if there's any remaining text in current_part, add it as the final piece.
    if current_part:
        message_parts.append(current_part)

    return message_parts


# ========================================================================
# STEP 1: TEST SUITE
# The test functions are defined below.
# ========================================================================

def test_short_text():
    """Tests a single line of text shorter than max_length."""
    print("Running: test_short_text")
    text = "This is a short message."
    max_length = 30
    expected = ["This is a short message."]
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_boundary_length_text():
    """Tests a single line of text with length equal to max_length."""
    print("Running: test_boundary_length_text")
    text = "This text is exactly 30 chars."
    max_length = 30
    expected = ["This text is exactly 30 chars."]
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_split_by_newline():
    """Tests grouping of multiple short lines using newlines as the primary separator."""
    print("Running: test_split_by_newline")
    text = "First line.\nSecond line.\nThird, slightly longer line."
    max_length = 30
    # "First line.\nSecond line." has length 24, so it gets grouped.
    # "Third, slightly longer line." has length 29 and forms the next part.
    expected = ["First line.\nSecond line.", "Third, slightly longer line."]
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_forced_split():
    """Tests a single long line with no newlines that must be forcefully split."""
    print("Running: test_forced_split")
    text = "This is a very long line of text that has no newlines and must be split forcefully."
    max_length = 30
    expected = [
        "This is a very long line of te",  # 30 characters
        "xt that has no newlines and mu",  # 30 characters
        "st be split forcefully."          # remaining 23 characters
    ]
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_case():
    """Tests a mix of short lines, newlines, and a very long line that requires forced splitting."""
    print("Running: test_complex_case")
    text = "Short line.\nThis is a very very very long second line that will need to be broken up.\nThird line."
    max_length = 30
    expected = [
        "Short line.",
        "This is a very very very long ",  # 30 characters (with space at end)
        "second line that will need to ",  # 30 characters (with space at end)
        "be broken up.",                    # remaining 13 characters
        "Third line."
    ]
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_empty_string():
    """Tests the behavior when the input text is an empty string."""
    print("Running: test_empty_string")
    text = ""
    max_length = 30
    expected = []
    result = split_message(text, max_length)
    assert result == expected, f"Expected {expected}, but got {result}"

# ========================================================================
# EXECUTION LOGIC
# This block runs all the defined tests.
# ========================================================================

if __name__ == "__main__":
    try:
        # Run all test functions
        test_short_text()
        test_boundary_length_text()
        test_split_by_newline()
        test_forced_split()
        test_complex_case()
        test_empty_string()

        # If all asserts pass, this message will be printed
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")