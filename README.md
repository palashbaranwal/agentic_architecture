# Math Agent Architecture: From 3 Files to 5 Files

This document explains the detailed process of converting the initial 3 files (`models.py`, `cot_tools.py`, and `agent_main.py`) into a more modular architecture with 5 files (`models.py`, `perceive.py`, `memory.py`, `decision.py`, `action.py`, and `agent_main.py`).

## Overview

The original architecture consisted of three main files:
1. `models.py` - Pydantic models for data validation
2. `cot_tools.py` - Implementation of mathematical operations and tools
3. `agent_main.py` - Main entry point with AI integration

The new architecture follows a more modular approach with five main files:
1. `models.py` - Pydantic models for data validation (unchanged)
2. `perceive.py` - Component responsible for receiving and interpreting input
3. `memory.py` - Component responsible for storing and retrieving information
4. `decision.py` - Component responsible for evaluating options and determining actions
5. `action.py` - Component responsible for executing actions to affect the environment
6. `agent_main.py` - Main agent class that integrates all components

## Detailed Conversion Process

### 1. `models.py`

**Status**: Unchanged

The `models.py` file was kept as is, as it already contained the Pydantic models needed for data validation. These models are used across all components of the agent.

### 2. `perceive.py` (New)

**Source**: Extracted from `cot_tools.py` and `agent_main.py`

The `perceive.py` file was created to handle all input processing and interpretation. It contains:

- **From `cot_tools.py`**:
  - The `parse_expression` method, which was extracted from the various calculation functions
  - The `parse_command` method, which was derived from the command handling logic in `agent_main.py`
  - The `open_paint` method, which was moved from `cot_tools.py`
  - The `create_thumbnail` method, which was moved from `cot_tools.py`

- **From `agent_main.py`**:
  - Input parsing logic that was previously embedded in the main file
  - Command interpretation logic that determined what action to take based on user input

The `Perceive` class is responsible for:
- Parsing mathematical expressions to identify operations and operands
- Parsing user commands to determine the intended action
- Opening Microsoft Paint and managing its state
- Creating image thumbnails

### 3. `memory.py` (New)

**Source**: Extracted from `agent_main.py` and `cot_tools.py`

The `memory.py` file was created to handle all storage and retrieval of information. It contains:

- **From `agent_main.py`**:
  - The conversation history tracking logic
  - The error pattern storage and retrieval logic
  - The user preference management logic

- **From `cot_tools.py`**:
  - The calculation history tracking logic
  - The Paint state management logic

The `Memory` class is responsible for:
- Loading and saving memory from/to a JSON file
- Adding calculations to history and retrieving calculation history
- Adding error patterns and retrieving error resolutions
- Setting and getting user preferences
- Setting and getting Paint state
- Storing and retrieving calculation steps

### 4. `decision.py` (New)

**Source**: Extracted from `cot_tools.py` and `agent_main.py`

The `decision.py` file was created to handle all decision-making logic. It contains:

- **From `cot_tools.py`**:
  - The operation selection logic that was previously embedded in the calculation functions
  - The verification logic that checked if calculations were correct
  - The consistency checking logic that analyzed calculation steps

- **From `agent_main.py`**:
  - The reasoning generation logic that created step-by-step explanations
  - The error handling logic that determined how to handle different types of errors

The `Decision` class is responsible for:
- Deciding which mathematical operation to perform based on an expression
- Verifying if a calculation is correct
- Checking if calculation steps are consistent with each other
- Generating fallback reasoning when primary reasoning fails
- Deciding how to handle different types of errors

### 5. `action.py` (New)

**Source**: Extracted from `cot_tools.py`

The `action.py` file was created to handle all action execution. It contains:

- **From `cot_tools.py`**:
  - All the mathematical operation functions (add, subtract, multiply, divide, etc.)
  - The Paint-related functions (open_paint, draw_rectangle, add_text_in_paint)
  - The special functions (strings_to_chars_to_int, int_list_to_exponential_sum, fibonacci_numbers)
  - The reasoning and verification functions (show_reasoning, verify, check_consistency, fallback_reasoning)

The `Action` class is responsible for:
- Executing basic math operations (addition, subtraction, multiplication, division, etc.)
- Executing special math operations (power, square root, cube root, factorial, etc.)
- Executing Paint-related operations (opening Paint, drawing rectangles, adding text)
- Executing reasoning and verification operations (showing reasoning, verifying calculations, checking consistency)
- Executing special functions (ASCII conversion, exponential sum, Fibonacci numbers)

### 6. `agent_main.py` (Modified)

**Source**: Modified from the original `agent_main.py`

The `agent_main.py` file was modified to integrate all the components. It contains:

- **From the original `agent_main.py`**:
  - The AI integration logic with Gemini
  - The main function that sets up the client session
  - The system prompt and conversation handling

- **New additions**:
  - The `MathAgent` class that integrates all components
  - Methods to process user input and route it to the appropriate component
  - Methods to handle different types of requests (calculation, verification, reasoning, etc.)
  - Example usage code that demonstrates how to use the agent

The `MathAgent` class is responsible for:
- Initializing all components (Perceive, Memory, Decision, Action)
- Processing user input and determining the appropriate action
- Routing requests to the appropriate component
- Maintaining the agent's state (current expression, result, steps)
- Providing a unified interface to all components

## Component Interactions

The new architecture follows a clear separation of concerns:

1. **Perceive** → **Decision**: The Perceive component parses user input and passes it to the Decision component to determine what action to take.

2. **Decision** → **Action**: The Decision component decides what action to take and passes the decision to the Action component to execute.

3. **Action** → **Memory**: The Action component executes actions and stores the results in the Memory component.

4. **Memory** → **Decision**: The Decision component uses the Memory component to retrieve information needed to make decisions.

5. **Memory** → **Action**: The Action component uses the Memory component to retrieve information needed to execute actions.

## Benefits of the New Architecture

1. **Modularity**: Each component has a clear responsibility and can be developed, tested, and maintained independently.

2. **Reusability**: Components can be reused in other agents or applications.

3. **Extensibility**: New functionality can be added by extending existing components or adding new ones.

4. **Testability**: Each component can be tested in isolation.

5. **Readability**: The code is more organized and easier to understand.

6. **Maintainability**: Changes to one component are less likely to affect others.

## Conclusion

The conversion from 3 files to 5 files represents a significant architectural improvement. The new architecture follows the principles of separation of concerns and modularity, making the code more maintainable, extensible, and testable. Each component has a clear responsibility and interacts with others in a well-defined way, resulting in a more robust and flexible agent. 