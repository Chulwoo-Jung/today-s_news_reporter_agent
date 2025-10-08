## TDD-Based Function Development
You are an expert Python developer who practices Test-Driven Development (TDD) using only the Python standard library. You will develop a function called split_message. According to TDD principles, you must write the test code before the actual implementation.

### Step 1: Write the Test Execution Script
Do not use any external libraries like pytest or unittest. You must write the test code using only assert statements and basic Python syntax.

Function Specification:
- Function Name: split_message
- Arguments: text (str), max_length (int)
- Return Value: list[str]

Core Requirements:
1. The function must split the given text into multiple strings, none of which exceeds max_length.
2. For readability, splitting should prioritize newline characters (\n).
3. If a single line without newlines exceeds max_length, that line must be forcefully split to fit within the max_length.

Request:
First, please write a single Python script (tdd.py) that verifies all of the following test scenarios.

1. At the top of the script, declare the target function split_message but leave its body empty with pass or a dummy value to ensure the script is runnable. (Dummy Function)
2. Create a separate test function (e.g., test_short_text()) to verify each of the cases below.
3. Inside each test function, call split_message and use an assert statement to confirm that the result matches the expected output.
4. At the end of the script, add execution logic that calls all test functions in sequence and prints "All tests passed!" if all assert statements pass.

Required Test Cases (assuming max_length=30):
- Basic: Text shorter than max_length.
- Boundary: Text with a length equal to max_length.
- Newline Splitting: Multi-line text that is appropriately grouped based on newlines.
- Forced Splitting: A long text with no newlines that is forcefully split.
- Complex: A mix of standard newline splitting and forced splitting.
- Empty String: The input is an empty string ("").

### Step 2: Implement the Function to Pass the Tests
Now, implement the actual logic for the split_message function so that the tdd.py script created in Step 1 executes successfully without any AssertionError and prints the message "All tests passed!".

You must adhere strictly to the provided function signature: def split_message(text: str, max_length: int) -> list[str]:.

Please add clear comments to your code for readability.

