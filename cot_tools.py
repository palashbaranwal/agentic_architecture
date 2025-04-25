from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import math
import re
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from models import (
    AddInput, AddOutput, SqrtInput, SqrtOutput, 
    StringsToIntsInput, StringsToIntsOutput, 
    ExpSumInput, ExpSumOutput,
    ShowReasoningInput, ShowReasoningOutput,
    CalculateInput, CalculateOutput,
    VerifyInput, VerifyOutput,
    CheckConsistencyInput, CheckConsistencyOutput,
    FallbackReasoningInput, FallbackReasoningOutput,
    SubtractInput, SubtractOutput,
    MultiplyInput, MultiplyOutput,
    DivideInput, DivideOutput,
    PowerInput, PowerOutput,
    CbrtInput, CbrtOutput,
    FactorialInput, FactorialOutput,
    LogInput, LogOutput,
    RemainderInput, RemainderOutput,
    SinInput, SinOutput,
    CosInput, CosOutput,
    TanInput, TanOutput,
    MineInput, MineOutput
)


console = Console()
mcp = FastMCP("CoTCalculator")


@mcp.tool()
def show_reasoning(input: ShowReasoningInput) -> ShowReasoningOutput:
    """Show the step-by-step reasoning process"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(input.steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    return ShowReasoningOutput(text="Reasoning shown")

@mcp.tool()
def calculate(input: CalculateInput) -> TextContent:
    """Calculate the result of an expression"""
    console.print("[blue]FUNCTION CALL:[/blue] calculate()")
    console.print(f"[blue]Expression:[/blue] {input.expression}")
    try:
        result = eval(input.expression)
        console.print(f"[green]Result:[/green] {result}")
        return TextContent(
            type="text",
            text=str(result)
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )

@mcp.tool()
def verify(input: VerifyInput) -> VerifyOutput:
    """Verify if a calculation is correct"""
    console.print("[blue]FUNCTION CALL:[/blue] verify()")
    console.print(f"[blue]Verifying:[/blue] {input.expression} = {input.expected}")
    try:
        actual = float(eval(input.expression))
        is_correct = abs(actual - float(input.expected)) < 1e-10
        
        if is_correct:
            console.print(f"[green]✓ Correct! {input.expression} = {input.expected}[/green]")
        else:
            console.print(f"[red]✗ Incorrect! {input.expression} should be {actual}, got {input.expected}[/red]")
            
        return VerifyOutput(text=str(is_correct))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return VerifyOutput(text=f"Error: {str(e)}")

@mcp.tool()
def check_consistency(input: CheckConsistencyInput) -> CheckConsistencyOutput:
    """Check if calculation steps are consistent with each other"""
    console.print("[blue]FUNCTION CALL:[/blue] check_consistency()")
    
    try:
        # Create a table for step analysis
        table = Table(
            title="Step-by-Step Consistency Analysis",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Step", style="cyan")
        table.add_column("Expression", style="blue")
        table.add_column("Result", style="green")
        table.add_column("Checks", style="yellow")

        issues = []
        warnings = []
        insights = []
        previous = None
        
        for i, (expression, result) in enumerate(input.steps, 1):
            checks = []
            
            # 1. Basic Calculation Verification
            try:
                expected = eval(expression)
                if abs(float(expected) - float(result)) < 1e-10:
                    checks.append("[green]✓ Calculation verified[/green]")
                else:
                    issues.append(f"Step {i}: Calculation mismatch")
                    checks.append("[red]✗ Calculation error[/red]")
            except:
                warnings.append(f"Step {i}: Couldn't verify calculation")
                checks.append("[yellow]! Verification failed[/yellow]")

            # 2. Dependency Analysis
            if previous:
                prev_expr, prev_result = previous
                if str(prev_result) in expression:
                    checks.append("[green]✓ Uses previous result[/green]")
                    insights.append(f"Step {i} builds on step {i-1}")
                else:
                    checks.append("[blue]○ Independent step[/blue]")

            # 3. Magnitude Check
            if previous and result != 0 and previous[1] != 0:
                ratio = abs(result / previous[1])
                if ratio > 1000:
                    warnings.append(f"Step {i}: Large increase ({ratio:.2f}x)")
                    checks.append("[yellow]! Large magnitude increase[/yellow]")
                elif ratio < 0.001:
                    warnings.append(f"Step {i}: Large decrease ({1/ratio:.2f}x)")
                    checks.append("[yellow]! Large magnitude decrease[/yellow]")

            # 4. Pattern Analysis
            operators = re.findall(r'[\+\-\*\/\(\)]', expression)
            if '(' in operators and ')' not in operators:
                warnings.append(f"Step {i}: Mismatched parentheses")
                checks.append("[red]✗ Invalid parentheses[/red]")

            # 5. Result Range Check
            if abs(result) > 1e6:
                warnings.append(f"Step {i}: Very large result")
                checks.append("[yellow]! Large result[/yellow]")
            elif abs(result) < 1e-6 and result != 0:
                warnings.append(f"Step {i}: Very small result")
                checks.append("[yellow]! Small result[/yellow]")

            # Add row to table
            table.add_row(
                f"Step {i}",
                expression,
                f"{result}",
                "\n".join(checks)
            )
            
            previous = (expression, result)

        # Display Analysis
        console.print("\n[bold cyan]Consistency Analysis Report[/bold cyan]")
        console.print(table)

        if issues:
            console.print(Panel(
                "\n".join(f"[red]• {issue}[/red]" for issue in issues),
                title="Critical Issues",
                border_style="red"
            ))

        if warnings:
            console.print(Panel(
                "\n".join(f"[yellow]• {warning}[/yellow]" for warning in warnings),
                title="Warnings",
                border_style="yellow"
            ))

        if insights:
            console.print(Panel(
                "\n".join(f"[blue]• {insight}[/blue]" for insight in insights),
                title="Analysis Insights",
                border_style="blue"
            ))

        # Final Consistency Score
        total_checks = len(input.steps) * 5  # 5 types of checks per step
        passed_checks = total_checks - (len(issues) * 2 + len(warnings))
        consistency_score = (passed_checks / total_checks) * 100

        console.print(Panel(
            f"[bold]Consistency Score: {consistency_score:.1f}%[/bold]\n" +
            f"Passed Checks: {passed_checks}/{total_checks}\n" +
            f"Critical Issues: {len(issues)}\n" +
            f"Warnings: {len(warnings)}\n" +
            f"Insights: {len(insights)}",
            title="Summary",
            border_style="green" if consistency_score > 80 else "yellow" if consistency_score > 60 else "red"
        ))

        return CheckConsistencyOutput(text=str({
            "consistency_score": consistency_score,
            "issues": issues,
            "warnings": warnings,
            "insights": insights
        }))
    except Exception as e:
        console.print(f"[red]Error in consistency check: {str(e)}[/red]")
        return CheckConsistencyOutput(text=f"Error: {str(e)}")

@mcp.tool()
def fallback_reasoning(input: FallbackReasoningInput) -> FallbackReasoningOutput:
    """Provide fallback reasoning when primary reasoning fails"""
    console.print("[blue]FUNCTION CALL:[/blue] fallback_reasoning()")
    console.print(f"[blue]Step Description:[/blue] {input.step_description}")
    
    # Create an error panel with the step description
    console.print(Panel(
        f"[yellow]Fallback triggered:[/yellow]\n{input.step_description}",
        title="Fallback Reasoning",
        border_style="red"
    ))
    
    return FallbackReasoningOutput(text="Fallback reasoning provided")


#addition tool
@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """Add two numbers"""
    print("CALLED: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)

@mcp.tool()
def sqrt(input: SqrtInput) -> SqrtOutput:
    """Square root of a number"""
    print("CALLED: sqrt(SqrtInput) -> SqrtOutput")
    return SqrtOutput(result=input.a ** 0.5)

# subtraction tool
@mcp.tool()
def subtract(input: SubtractInput) -> SubtractOutput:
    """Subtract two numbers"""
    print("CALLED: subtract(SubtractInput) -> SubtractOutput")
    return SubtractOutput(result=input.a - input.b)

# multiplication tool
@mcp.tool()
def multiply(input: MultiplyInput) -> MultiplyOutput:
    """Multiply two numbers"""
    print("CALLED: multiply(MultiplyInput) -> MultiplyOutput")
    return MultiplyOutput(result=input.a * input.b)

#  division tool
@mcp.tool() 
def divide(input: DivideInput) -> DivideOutput:
    """Divide two numbers"""
    print("CALLED: divide(DivideInput) -> DivideOutput")
    return DivideOutput(result=input.a / input.b)

# power tool
@mcp.tool()
def power(input: PowerInput) -> PowerOutput:
    """Power of two numbers"""
    print("CALLED: power(PowerInput) -> PowerOutput")
    return PowerOutput(result=input.a ** input.b)


# cube root tool
@mcp.tool()
def cbrt(input: CbrtInput) -> CbrtOutput:
    """Cube root of a number"""
    print("CALLED: cbrt(CbrtInput) -> CbrtOutput")
    return CbrtOutput(result=input.a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(input: FactorialInput) -> FactorialOutput:
    """factorial of a number"""
    print("CALLED: factorial(FactorialInput) -> FactorialOutput")
    return FactorialOutput(result=math.factorial(input.a))

# log tool
@mcp.tool()
def log(input: LogInput) -> LogOutput:
    """log of a number"""
    print("CALLED: log(LogInput) -> LogOutput")
    return LogOutput(result=math.log(input.a))

# remainder tool
@mcp.tool()
def remainder(input: RemainderInput) -> RemainderOutput:
    """remainder of two numbers divison"""
    print("CALLED: remainder(RemainderInput) -> RemainderOutput")
    return RemainderOutput(result=input.a % input.b)

# sin tool
@mcp.tool()
def sin(input: SinInput) -> SinOutput:
    """sin of a number"""
    print("CALLED: sin(SinInput) -> SinOutput")
    return SinOutput(result=math.sin(input.a))

# cos tool
@mcp.tool()
def cos(input: CosInput) -> CosOutput:
    """cos of a number"""
    print("CALLED: cos(CosInput) -> CosOutput")
    return CosOutput(result=math.cos(input.a))

# tan tool
@mcp.tool()
def tan(input: TanInput) -> TanOutput:
    """tan of a number"""
    print("CALLED: tan(TanInput) -> TanOutput")
    return TanOutput(result=math.tan(input.a))

# mine tool
@mcp.tool()
def mine(input: MineInput) -> MineOutput:
    """special mining tool"""
    print("CALLED: mine(MineInput) -> MineOutput")
    return MineOutput(result=input.a - input.b - input.b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return StringsToIntsOutput(ascii_values=ascii_values)

@mcp.tool()
def int_list_to_exponential_sum(input: ExpSumInput) -> ExpSumOutput:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(ExpSumInput) -> ExpSumOutput")
    result = sum(math.exp(i) for i in input.int_list)
    return ExpSumOutput(result=result)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width to adjust coordinates
        primary_width = GetSystemMetrics(0)
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.2)
        
        # Click on the Rectangle tool using the correct coordinates for secondary screen
        paint_window.click_input(coords=(530, 82 ))
        time.sleep(0.2)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Draw rectangle - coordinates should already be relative to the Paint window
        # No need to add primary_width since we're clicking within the Paint window
        canvas.press_mouse_input(coords=(x1+2560, y1))
        canvas.move_mouse_input(coords=(x2+2560, y2))
        canvas.release_mouse_input(coords=(x2+2560, y2))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        # Click on the Rectangle tool
        paint_window.click_input(coords=(528, 92))
        time.sleep(0.5)
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        paint_window.type_keys('t')
        time.sleep(0.1)
        paint_window.type_keys('x')
        time.sleep(0.5)
        
        # Click where to start typing
        canvas.click_input(coords=(810, 533))
        time.sleep(0.5)
        
        # Type the text passed from client
        paint_window.type_keys(text)
        time.sleep(0.5)
        
        # Click to exit text mode
        canvas.click_input(coords=(1050, 800))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on secondary monitor"""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(0.2)
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Get primary monitor width
        primary_width = GetSystemMetrics(0)
        
        # First move to secondary monitor without specifying size
        win32gui.SetWindowPos(
            paint_window.handle,
            win32con.HWND_TOP,
            primary_width + 1, 0,  # Position it on secondary monitor
            0, 0,  # Let Windows handle the size
            win32con.SWP_NOSIZE  # Don't change the size
        )
        
        # Now maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(0.2)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully on secondary monitor and maximized"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    import sys
    # Check if running with mcp dev command
    print("STARTING THE SERVER AT AMAZING LOCATION")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution




# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1 and sys.argv[1] == "dev":
#         mcp.run()
#     else:
#         mcp.run(transport="stdio")
