import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
import asyncio
from rich.console import Console
from rich.panel import Panel
import json
from typing import Tuple, Optional, Dict, Any, List, Union
import math
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import time
from mcp.types import TextContent
from mcp.server.fastmcp import FastMCP
from mcp import types
from PIL import Image as PILImage
from pywinauto.application import Application
import win32gui
import win32con

# Import our components
from perceive import Perceive
from memory import Memory
from decision import Decision
from action import Action
from models import (
    VerifyInput, VerifyOutput,
    CheckConsistencyInput, CheckConsistencyOutput,
    ShowReasoningInput, ShowReasoningOutput,
    AddInput, AddOutput,
    SubtractInput, SubtractOutput,
    MultiplyInput, MultiplyOutput,
    DivideInput, DivideOutput,
    PowerInput, PowerOutput,
    SqrtInput, SqrtOutput,
    CbrtInput, CbrtOutput,
    FactorialInput, FactorialOutput,
    LogInput, LogOutput,
    RemainderInput, RemainderOutput,
    SinInput, SinOutput,
    CosInput, CosOutput,
    TanInput, TanOutput,
    MineInput, MineOutput,
    StringsToIntsInput, StringsToIntsOutput,
    ExpSumInput, ExpSumOutput,
    FallbackReasoningInput, FallbackReasoningOutput
)

console = Console()

# Load environment variables and setup Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

mcp = FastMCP("MathAgent")

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        return response
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None

async def get_llm_response(client, prompt):
    """Get response from LLM with timeout"""
    response = await generate_with_timeout(client, prompt)
    if response and response.text:
        return response.text.strip()
    return None

def validate_json(function_call: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Validates the JSON structure in a function call string.
    
    Args:
        function_call: String starting with 'FUNCTION_CALL: ' followed by JSON
        
    Returns:
        Tuple containing:
        - bool: Whether validation passed
        - Optional[Dict]: Parsed JSON if valid, None if invalid
        - str: Validation message
    """
    try:
        # Extract JSON part after FUNCTION_CALL:
        if not function_call.startswith("FUNCTION_CALL: "):
            return False, None, "Invalid format: Must start with 'FUNCTION_CALL: '"
            
        json_str = function_call.replace("FUNCTION_CALL: ", "", 1)
        
        # Parse JSON
        parsed_json = json.loads(json_str)
        
        # Validate required fields
        if not isinstance(parsed_json, dict):
            return False, None, "Invalid JSON: Must be an object"
            
        if "name" not in parsed_json:
            return False, None, "Missing required field: 'name'"
            
        if not isinstance(parsed_json["name"], str):
            return False, None, "Invalid field: 'name' must be a string"
            
        if "args" not in parsed_json:
            return False, None, "Missing required field: 'args'"
            
        if not isinstance(parsed_json["args"], dict):
            return False, None, "Invalid field: 'args' must be an object"
            
        return True, parsed_json, "Validation successful"
        
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"

async def handle_tool_error(session, error_msg: str, step_context: str) -> str:
    """
    Handle tool errors by calling fallback_reasoning
    Returns the fallback message for the conversation
    """
    fallback_description = f"Error in step: {step_context}\nError details: {error_msg}"
    await session.call_tool("fallback_reasoning", arguments={"step_description": fallback_description})
    return f"\nUser: Error occurred. Fallback triggered. Please reconsider this step or try an alternative approach."

class MathAgent:
    """Main agent class that integrates all components."""
    
    def __init__(self, memory_path: str = "agent_memory.json"):
        # Initialize components
        self.memory = Memory(storage_path=memory_path)
        self.perceive = Perceive()
        self.decision = Decision(self.memory)
        self.action = Action(self.memory, self.perceive)
        self.register_tools()
        
        # Agent state
        self.current_expression = None
        self.current_result = None
        self.current_steps = []
        
        console.print(Panel(
            "[bold green]Math Agent Initialized[/bold green]\n" +
            "Ready to perform calculations, reasoning, and Paint operations.",
            title="Math Agent",
            border_style="green"
        ))
    
    def register_tools(self):
        """Register all tools with FastMCP."""
        
        @mcp.tool()
        def calculate(expression: str) -> TextContent:
            return self.action.calculate(expression)
        
        @mcp.tool()
        def verify(input: VerifyInput) -> VerifyOutput:
            result = self.action.verify(input.expression, input.expected)
            return VerifyOutput(text=result.text)
        
        @mcp.tool()
        def check_consistency(input: CheckConsistencyInput) -> CheckConsistencyOutput:
            result = self.action.check_consistency(input.steps)
            return CheckConsistencyOutput(text=result.text)
        
        @mcp.tool()
        def show_reasoning(input: ShowReasoningInput) -> ShowReasoningOutput:
            result = self.action.show_reasoning(input.steps)
            return ShowReasoningOutput(text=result.text)
        
        @mcp.tool()
        def add(input: AddInput) -> AddOutput:
            result = self.action.add(input.a, input.b)
            return AddOutput(result=result)
        
        @mcp.tool()
        def subtract(input: SubtractInput) -> SubtractOutput:
            result = self.action.subtract(input.a, input.b)
            return SubtractOutput(result=result)
        
        @mcp.tool()
        def multiply(input: MultiplyInput) -> MultiplyOutput:
            result = self.action.multiply(input.a, input.b)
            return MultiplyOutput(result=result)
        
        @mcp.tool()
        def divide(input: DivideInput) -> DivideOutput:
            result = self.action.divide(input.a, input.b)
            return DivideOutput(result=result)
        
        @mcp.tool()
        def power(input: PowerInput) -> PowerOutput:
            result = self.action.power(input.a, input.b)
            return PowerOutput(result=result)
        
        @mcp.tool()
        def sqrt(input: SqrtInput) -> SqrtOutput:
            result = self.action.sqrt(input.a)
            return SqrtOutput(result=result)
        
        @mcp.tool()
        def cbrt(input: CbrtInput) -> CbrtOutput:
            result = self.action.cbrt(input.a)
            return CbrtOutput(result=result)
        
        @mcp.tool()
        def factorial(input: FactorialInput) -> FactorialOutput:
            result = self.action.factorial(input.a)
            return FactorialOutput(result=result)
        
        @mcp.tool()
        def log(input: LogInput) -> LogOutput:
            result = self.action.log(input.a)
            return LogOutput(result=result)
        
        @mcp.tool()
        def remainder(input: RemainderInput) -> RemainderOutput:
            result = self.action.remainder(input.a, input.b)
            return RemainderOutput(result=result)
        
        @mcp.tool()
        def sin(input: SinInput) -> SinOutput:
            result = self.action.sin(input.a)
            return SinOutput(result=result)
        
        @mcp.tool()
        def cos(input: CosInput) -> CosOutput:
            result = self.action.cos(input.a)
            return CosOutput(result=result)
        
        @mcp.tool()
        def tan(input: TanInput) -> TanOutput:
            result = self.action.tan(input.a)
            return TanOutput(result=result)
        
        @mcp.tool()
        def mine(input: MineInput) -> MineOutput:
            result = self.action.mine(input.a, input.b)
            return MineOutput(result=result)
        
        # @mcp.tool()
        # def create_thumbnail(image_path: str) -> types.Image:
        #     img = self.action.create_thumbnail(image_path)
        #     return types.Image(data=img.tobytes(), format="png")
        
        @mcp.tool()
        def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
            result = self.action.strings_to_chars_to_int(input.string)
            return StringsToIntsOutput(result=result)
        
        @mcp.tool()
        def int_list_to_exponential_sum(input: ExpSumInput) -> ExpSumOutput:
            result = self.action.int_list_to_exponential_sum(input.int_list)
            return ExpSumOutput(result=result)
        
        @mcp.tool()
        def fibonacci_numbers(n: int) -> list:
            return self.action.fibonacci_numbers(n)
        
        # @mcp.tool()
        # async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
        #     return await self.action.draw_rectangle(x1, y1, x2, y2)
        
        # @mcp.tool()
        # async def add_text_in_paint(text: str) -> dict:
        #     return await self.action.add_text_in_paint(text)
        
        # @mcp.tool()
        # async def open_paint() -> dict:
        #     return await self.action.open_paint()
    
    def process_input(self, user_input: str) -> Dict[str, List[TextContent]]:
        """Process user input and determine the appropriate action."""
        console.print(f"[bold blue]User Input:[/bold blue] {user_input}")
        
        # Parse the input to determine the intended action
        parsed_input = self.perceive.parse_command(user_input)
        action_type = parsed_input.get('action', 'calculate')
        
        # Handle different action types
        if action_type == 'calculate':
            expression = parsed_input.get('expression', user_input)
            return self.handle_calculation(expression)
        
        elif action_type == 'verify':
            expression = parsed_input.get('expression', '')
            expected = parsed_input.get('expected', 0.0)
            return self.handle_verification(expression, expected)
        
        elif action_type == 'reason':
            expression = parsed_input.get('expression', user_input)
            return self.handle_reasoning(expression)
        
        elif action_type == 'check_consistency':
            steps = parsed_input.get('steps', self.current_steps)
            return self.handle_consistency_check(steps)
        
        elif action_type == 'draw_rectangle':
            x1 = parsed_input.get('x1', 0)
            y1 = parsed_input.get('y1', 0)
            x2 = parsed_input.get('x2', 100)
            y2 = parsed_input.get('y2', 100)
            return self.action.draw_rectangle(x1, y1, x2, y2)
        
        elif action_type == 'add_text':
            text = parsed_input.get('text', '')
            return self.action.add_text_in_paint(text)
        
        elif action_type == 'open_paint':
            return self.action.open_paint()
        
        else:
            # Default to calculating the expression
            return self.handle_calculation(user_input)
    
    def handle_calculation(self, expression: str) -> Dict[str, List[TextContent]]:
        """Handle calculation requests."""
        console.print(f"[bold cyan]Calculating:[/bold cyan] {expression}")
        
        # Decide which operation to perform
        operation, operands = self.decision.decide_operation(expression)
        
        # Execute the appropriate action
        if operation == 'add':
            result = self.action.add(operands[0], operands[1])
        elif operation == 'subtract':
            result = self.action.subtract(operands[0], operands[1])
        elif operation == 'multiply':
            result = self.action.multiply(operands[0], operands[1])
        elif operation == 'divide':
            result = self.action.divide(operands[0], operands[1])
        elif operation == 'power':
            result = self.action.power(operands[0], operands[1])
        elif operation == 'sqrt':
            result = self.action.sqrt(operands[0])
        elif operation == 'cbrt':
            result = self.action.cbrt(operands[0])
        elif operation == 'factorial':
            result = self.action.factorial(operands[0])
        elif operation == 'log':
            result = self.action.log(operands[0])
        elif operation == 'remainder':
            result = self.action.remainder(operands[0], operands[1])
        elif operation == 'sin':
            result = self.action.sin(operands[0])
        elif operation == 'cos':
            result = self.action.cos(operands[0])
        elif operation == 'tan':
            result = self.action.tan(operands[0])
        elif operation == 'mine':
            result = self.action.mine(operands[0], operands[1])
        else:
            # Use the calculate function for complex expressions
            return {
                "content": [self.action.calculate(expression)]
            }
        
        # Store the current state
        self.current_expression = expression
        self.current_result = result
        
        # Create a step for reasoning
        step = f"{expression} = {result}"
        self.current_steps.append(step)
        
        # Store in memory
        self.memory.add_calculation(expression, result, [step])
        
        # Return the result
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"{expression} = {result}"
                )
            ]
        }
    
    def handle_verification(self, expression: str, expected: float) -> Dict[str, List[TextContent]]:
        """Handle verification requests."""
        console.print(f"[bold cyan]Verifying:[/bold cyan] {expression} = {expected}")
        
        # Use the action component to verify
        result = self.action.verify(expression, expected)
        
        # Store in memory
        self.memory.add_calculation(expression, expected, [f"{expression} = {expected}"])
        
        return {
            "content": [result]
        }
    
    def handle_reasoning(self, expression: str) -> Dict[str, List[TextContent]]:
        """Handle reasoning requests."""
        console.print(f"[bold cyan]Reasoning about:[/bold cyan] {expression}")
        
        # Generate steps for the expression
        steps = self.generate_reasoning_steps(expression)
        
        # Store the steps
        self.current_steps = steps
        
        # Show the reasoning
        result = self.action.show_reasoning(steps)
        
        return {
            "content": [result]
        }
    
    def handle_consistency_check(self, steps: List[str]) -> Dict[str, List[TextContent]]:
        """Handle consistency check requests."""
        console.print(f"[bold cyan]Checking consistency of {len(steps)} steps[/bold cyan]")
        
        # If steps is a string, try to parse it into a list
        if isinstance(steps, str):
            # Try to split by comma if it's a comma-separated string
            if ',' in steps:
                steps = [step.strip() for step in steps.split(',')]
            else:
                # Otherwise treat it as a single step
                steps = [steps.strip()]
        
        # Use the action component to check consistency
        result = self.action.check_consistency(steps)
        
        return {
            "content": [result]
        }
    
    def generate_reasoning_steps(self, expression: str) -> List[str]:
        """Generate step-by-step reasoning for an expression."""
        try:
            # Parse the expression
            parsed = self.perceive.parse_expression(expression)
            
            if parsed.get('operation') == 'error':
                # If parsing failed, use fallback reasoning
                return [f"Error parsing expression: {parsed.get('message')}"]
            
            # Generate steps based on the operation
            if parsed.get('operation') == 'add':
                a, b = parsed.get('operands', [0, 0])
                return [
                    f"{a} + {b} = {a + b}"
                ]
            elif parsed.get('operation') == 'subtract':
                a, b = parsed.get('operands', [0, 0])
                return [
                    f"{a} - {b} = {a - b}"
                ]
            elif parsed.get('operation') == 'multiply':
                a, b = parsed.get('operands', [0, 0])
                return [
                    f"{a} * {b} = {a * b}"
                ]
            elif parsed.get('operation') == 'divide':
                a, b = parsed.get('operands', [0, 0])
                if b == 0:
                    return ["Cannot divide by zero"]
                return [
                    f"{a} / {b} = {a / b}"
                ]
            elif parsed.get('operation') == 'power':
                a, b = parsed.get('operands', [0, 0])
                return [
                    f"{a} ^ {b} = {a ** b}"
                ]
            elif parsed.get('operation') == 'sqrt':
                a = parsed.get('operands', [0])[0]
                if a < 0:
                    return ["Cannot take square root of negative number"]
                return [
                    f"sqrt({a}) = {a ** 0.5}"
                ]
            elif parsed.get('operation') == 'cbrt':
                a = parsed.get('operands', [0])[0]
                return [
                    f"cbrt({a}) = {a ** (1/3)}"
                ]
            elif parsed.get('operation') == 'factorial':
                a = parsed.get('operands', [0])[0]
                if a < 0:
                    return ["Cannot take factorial of negative number"]
                if not isinstance(a, int):
                    return ["Factorial is only defined for integers"]
                return [
                    f"{a}! = {math.factorial(a)}"
                ]
            elif parsed.get('operation') == 'log':
                a = parsed.get('operands', [0])[0]
                if a <= 0:
                    return ["Cannot take log of non-positive number"]
                return [
                    f"log({a}) = {math.log(a)}"
                ]
            elif parsed.get('operation') == 'remainder':
                a, b = parsed.get('operands', [0, 0])
                if b == 0:
                    return ["Cannot take remainder when divisor is zero"]
                return [
                    f"{a} % {b} = {a % b}"
                ]
            elif parsed.get('operation') == 'sin':
                a = parsed.get('operands', [0])[0]
                return [
                    f"sin({a}) = {math.sin(a)}"
                ]
            elif parsed.get('operation') == 'cos':
                a = parsed.get('operands', [0])[0]
                return [
                    f"cos({a}) = {math.cos(a)}"
                ]
            elif parsed.get('operation') == 'tan':
                a = parsed.get('operands', [0])[0]
                return [
                    f"tan({a}) = {math.tan(a)}"
                ]
            elif parsed.get('operation') == 'mine':
                a, b = parsed.get('operands', [0, 0])
                return [
                    f"mine({a}, {b}) = {a - b - b}"
                ]
            else:
                # For complex expressions, use the calculate function
                try:
                    result = eval(expression)
                    return [
                        f"{expression} = {result}"
                    ]
                except Exception as e:
                    # If calculation fails, use fallback reasoning
                    return [f"Error calculating expression: {str(e)}"]
        except Exception as e:
            # If anything fails, use fallback reasoning
            return [f"Error generating reasoning: {str(e)}"]
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get calculation history."""
        return self.memory.get_calculation_history(limit)
    
    def get_error_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get error patterns."""
        return self.memory.error_patterns
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return self.memory.user_preferences
    
    def get_paint_state(self) -> Optional[Dict[str, Any]]:
        """Get Paint state."""
        return self.memory.get_paint_state()

async def main():
    try:
        console.print(Panel("Chain of Thought Calculator", border_style="cyan"))

        server_params = StdioServerParameters(
            command="python",
            args=["math_tools.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                system_prompt = """You are a mathematical reasoning agent that solves problems step by step, tags the reasoning type, performs internal self-checks, and uses tools when appropriate.
                You have access to these tools:
                show_reasoning(steps: list) - Display your reasoning steps. Each step must include a label for the type of reasoning (e.g., arithmetic, logic, pattern).
                calculate(expression: str)- Calculate the result of an expression.
                verify(expression: str, expected: float) - Check if a calculation is correct.
                fallback(reason: str) - Use this if a tool fails or you are uncertain how to proceed.

                
                Instructions:
                1. Always start with reasoning. Use show_reasoning to break down the problem with labeled steps. This is mandatory for all the prompt you might get.
                2. Tag each step with the type of reasoning used: Eg: ""Arithmetic", "Logical" and "Entity Lookup". This is mandatory for all step.
                3. Then calculate using calculate().
                4. After each calculation, verify using verify().
                5. If you are unsure, or a tool result is inconsistent, call fallback() with an explanation.
                6. Before giving the final answer, re-check the logic and calculations, and state explicitly if they pass self-checks.
                7. Respond with exactly ONE line in one of the following formats:
                        FUNCTION_CALL: {"name": "function_name", "args": {"arg1": "value1", "arg2": "value2", ...}}
                        FINAL_ANSWER: [answer]


                Example:
                User: Solve (2 + 3) * 4
                Assistant: FUNCTION_CALL: show_reasoning|["1. First, solve inside parentheses: 2 + 3", "2. Then multiply the result by 4"]
                User: Next step?
                Assistant: FUNCTION_CALL: {"name":"calculate","args":{"expression":"2 + 3"}}
                User: Result is 5. Let's verify this step.
                Assistant: FUNCTION_CALL: {"name":"verify","args":{"expression":"2 + 3","expected":5}}
                User: Verified. Next step?
                Assistant: FUNCTION_CALL: {"name":"calculate","args":{"expression":"5 * 4"}}
                User: Result is 20. Let's verify the final answer.
                Assistant: FUNCTION_CALL: {"name":"verify","args":{"expression":"(2 + 3) * 4","expected":20}}
                User: Verified correct.
                Assistant: FINAL_ANSWER: [20]"""

                problem = "(23 + 7) * (15 - 8) * (12.5/25.0)"
                # problem = """Get the ASCII values of all characters in the word "INDIA", then compute the sum of exponentials of those ASCII values."""

                console.print(Panel(f"Problem: {problem}", border_style="cyan"))

                # Initialize conversation
                prompt = f"{system_prompt}\n\nSolve this problem step by step: {problem}"
                conversation_history = []

                while True:
                    response = await generate_with_timeout(client, prompt)
                    if not response or not response.text:
                        break

                    result = response.text.strip()
                    console.print(f"\n[yellow]Assistant:[/yellow] {result}")

                    if result.startswith("FUNCTION_CALL:"):
                        # Validate JSON first
                        is_valid, parsed_json, validation_message = validate_json(result)
                        
                        try:
                            if parsed_json:
                                func_name = parsed_json["name"]
                                args = parsed_json["args"]
                                
                                if func_name == "show_reasoning":
                                    try:
                                        steps = args.get("steps", [])
                                        await session.call_tool("show_reasoning", arguments={"steps": steps})
                                        prompt += f"\nUser: Next step?"
                                    except Exception as e:
                                        prompt += await handle_tool_error(
                                            session, 
                                            str(e), 
                                            f"show_reasoning with steps: {steps}"
                                        )
                                        
                                elif func_name == "calculate":
                                    try:
                                        expression = args.get("expression", "")
                                        calc_result = await session.call_tool("calculate", arguments={"expression": expression})
                                        
                                        if calc_result.content:
                                            value = calc_result.content[0].text
                                            
                                            # Self-check with fallback
                                            try:
                                                self_check_prompt = f"""Given the calculation:
                                                Expression: {expression}
                                                Result: {value}
                                                
                                                Is the result reasonable?

                                                Respond with ONLY 'YES' if all checks pass, or explain why they don't pass.
                                                """
                                                
                                                self_check_response = await get_llm_response(client, self_check_prompt)
                                                
                                                if not self_check_response:
                                                    prompt += await handle_tool_error(
                                                        session,
                                                        "Self-check failed to respond",
                                                        f"self-check for calculation: {expression} = {value}"
                                                    )
                                                elif self_check_response.strip() != "YES":
                                                    # Call fallback but continue with verification
                                                    await session.call_tool("fallback_reasoning", arguments={
                                                        "step_description": f"Self-check concerns: {self_check_response}"
                                                    })
                                            
                                            except Exception as e:
                                                prompt += await handle_tool_error(
                                                    session,
                                                    str(e),
                                                    f"self-check for calculation: {expression}"
                                                )
                                            
                                            prompt += f"\nUser: Result is {value}. Let's verify this step."
                                            conversation_history.append((expression, float(value)))
                                        else:
                                            prompt += await handle_tool_error(
                                                session,
                                                "No calculation result returned",
                                                f"calculate: {expression}"
                                            )
                                            
                                    except Exception as e:
                                        prompt += await handle_tool_error(
                                            session,
                                            str(e),
                                            f"calculate: {expression}"
                                        )
                                        
                                elif func_name == "verify":
                                    try:
                                        expression = args.get("expression", "")
                                        expected = float(args.get("expected", 0))
                                        verify_result = await session.call_tool("verify", arguments={
                                            "expression": expression,
                                            "expected": expected
                                        })
                                        
                                        if verify_result.content and verify_result.content[0].text.lower() == "false":
                                            # Verification failed, trigger fallback
                                            await session.call_tool("fallback_reasoning", arguments={
                                                "step_description": f"Verification failed for {expression} = {expected}"
                                            })
                                        
                                        prompt += f"\nUser: Verification completed. Next step?"
                                        
                                    except Exception as e:
                                        prompt += await handle_tool_error(
                                            session,
                                            str(e),
                                            f"verify: {expression} = {expected}"
                                        )
                                    
                                elif func_name == "fallback_reasoning":
                                    # Direct fallback call from LLM
                                    try:
                                        step_description = args.get("step_description", "")
                                        await session.call_tool("fallback_reasoning", arguments={
                                            "step_description": step_description
                                        })
                                        prompt += "\nUser: Fallback processed. Please proceed with an alternative approach."
                                    except Exception as e:
                                        console.print(f"[red]Error in fallback handling: {e}[/red]")
                                
                        except Exception as e:
                            prompt += await handle_tool_error(
                                session,
                                str(e),
                                "general tool execution"
                            )

                    elif result.startswith("FINAL_ANSWER:"):
                        # Verify the final answer against the original problem
                        if conversation_history:
                            final_answer = float(result.split("[")[1].split("]")[0])
                            await session.call_tool("verify", arguments={
                                "expression": problem,
                                "expected": final_answer
                            })
                        break
                    
                    prompt += f"\nAssistant: {result}"

                console.print("\n[green]Calculation completed![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    # Create the agent
    agent = MathAgent()
    
    # Example calculations
    print("\n=== Basic Calculations ===")
    agent.process_input("2 + 3")
    agent.process_input("10 - 4")
    agent.process_input("5 * 6")
    agent.process_input("20 / 4")
    
    # Example reasoning
    print("\n=== Reasoning ===")
    agent.process_input("reason 2 + 3")
    
    # Example verification
    print("\n=== Verification ===")
    agent.process_input("verify 2 + 3 = 5")
    
    # Example consistency check
    print("\n=== Consistency Check ===")
    agent.process_input("consistency 2 + 3 = 5, 5 * 2 = 10")
    
    # Example Paint operations
    # print("\n=== Paint Operations ===")
    # agent.process_input("open_paint")
    # agent.process_input("draw rectangle 100 100 300 200")
    # agent.process_input("add text Hello World")
    
    # Example history
    print("\n=== History ===")
    history = agent.get_history()
    for item in history:
        print(f"{item['expression']} = {item['result']}")

    asyncio.run(main())
