from mcp.types import TextContent
from mcp import types
from typing import List, Dict, Any, Union
import math
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from pywinauto.application import Application
import win32gui
import win32con
import time
from PIL import Image as PILImage

console = Console()

class Action:
    """Component responsible for executing actions to affect the environment."""
    
    def __init__(self, memory, perceive):
        self.memory = memory
        self.perceive = perceive
        self.paint_app = None
    
    def calculate(self, expression: str) -> TextContent:
        """Calculate the result of an expression."""
        console.print("[blue]FUNCTION CALL:[/blue] calculate()")
        console.print(f"[blue]Expression:[/blue] {expression}")
        try:
            result = eval(expression)
            console.print(f"[green]Result:[/green] {result}")
            
            # Store in memory
            self.memory.add_calculation(expression, result)
            
            return TextContent(
                type="text",
                text=str(result)
            )
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            
            # Store error in memory
            self.memory.add_error_pattern(type(e).__name__, str(e), "Try simplifying the expression")
            
            return TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] add()")
        result = a + b
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] subtract()")
        result = a - b
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] multiply()")
        result = a * b
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] divide()")
        if b == 0:
            raise ValueError("Division by zero")
        result = a / b
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def power(self, a: float, b: float) -> float:
        """Power of two numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] power()")
        result = math.pow(a, b)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def sqrt(self, a: float) -> float:
        """Square root of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] sqrt()")
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def cbrt(self, a: float) -> float:
        """Cube root of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] cbrt()")
        result = math.cbrt(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def factorial(self, a: int) -> int:
        """Factorial of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] factorial()")
        if a < 0:
            raise ValueError("Cannot calculate factorial of negative number")
        if not float(a).is_integer():
            raise ValueError("Factorial is only defined for integers")
        result = math.factorial(int(a))
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def log(self, a: float) -> float:
        """Log of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] log()")
        if a <= 0:
            raise ValueError("Cannot calculate logarithm of non-positive number")
        result = math.log(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def remainder(self, a: float, b: float) -> float:
        """Remainder of two numbers division."""
        console.print("[blue]FUNCTION CALL:[/blue] remainder()")
        if b == 0:
            raise ValueError("Division by zero")
        result = a % b
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def sin(self, a: float) -> float:
        """Sin of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] sin()")
        result = math.sin(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def cos(self, a: float) -> float:
        """Cos of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] cos()")
        result = math.cos(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def tan(self, a: float) -> float:
        """Tan of a number."""
        console.print("[blue]FUNCTION CALL:[/blue] tan()")
        result = math.tan(a)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def mine(self, a: float, b: float) -> float:
        """Special mining tool."""
        console.print("[blue]FUNCTION CALL:[/blue] mine()")
        result = min(a, b)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def show_reasoning(self, steps: List[str]) -> TextContent:
        """Show the step-by-step reasoning process."""
        console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
        for i, step in enumerate(steps, 1):
            console.print(Panel(
                f"{step}",
                title=f"Step {i}",
                border_style="cyan"
            ))
        return TextContent(
            type="text",
            text="Reasoning shown"
        )
    
    def verify(self, expression: str, expected: float) -> TextContent:
        """Verify if a calculation is correct."""
        console.print("[blue]FUNCTION CALL:[/blue] verify()")
        console.print(f"[blue]Verifying:[/blue] {expression} = {expected}")
        try:
            actual = float(eval(expression))
            is_correct = abs(actual - float(expected)) < 1e-10
            
            if is_correct:
                console.print(f"[green]✓ Correct! {expression} = {expected}[/green]")
            else:
                console.print(f"[red]✗ Incorrect! {expression} should be {actual}, got {expected}[/red]")
                
            return TextContent(
                type="text",
                text=str(is_correct)
            )
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            return TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
    
    def check_consistency(self, steps: List[str]) -> TextContent:
        """Check if calculation steps are consistent with each other."""
        console.print("[blue]FUNCTION CALL:[/blue] check_consistency()")
        
        # Store steps in memory for potential future use
        self.memory.store_steps(steps)
        
        # Use the decision component to check consistency
        from decision import Decision
        decision = Decision(self.memory)
        report = decision.check_consistency(steps)
        
        # Display the report
        console.print("\n[bold cyan]Consistency Analysis Report[/bold cyan]")
        console.print(report["table"])
        
        if report["issues"]:
            console.print(Panel(
                "\n".join(f"[red]• {issue}[/red]" for issue in report["issues"]),
                title="Critical Issues",
                border_style="red"
            ))
        
        if report["warnings"]:
            console.print(Panel(
                "\n".join(f"[yellow]• {warning}[/yellow]" for warning in report["warnings"]),
                title="Warnings",
                border_style="yellow"
            ))
        
        if report["insights"]:
            console.print(Panel(
                "\n".join(f"[blue]• {insight}[/blue]" for insight in report["insights"]),
                title="Analysis Insights",
                border_style="blue"
            ))
        
        # Calculate consistency score
        total_checks = len(steps) * 5  # 5 types of checks per step
        passed_checks = total_checks - (len(report["issues"]) * 2 + len(report["warnings"]))
        consistency_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        console.print(Panel(
            f"[bold]Consistency Score: {consistency_score:.1f}%[/bold]\n" +
            f"Passed Checks: {passed_checks}/{total_checks}\n" +
            f"Critical Issues: {len(report['issues'])}\n" +
            f"Warnings: {len(report['warnings'])}\n" +
            f"Insights: {len(report['insights'])}",
            title="Summary",
            border_style="green" if consistency_score > 80 else "yellow" if consistency_score > 60 else "red"
        ))
        
        return TextContent(
            type="text",
            text=f"Consistency check completed. Score: {consistency_score:.1f}%"
        )
    
    def fallback_reasoning(self, step_description: str) -> TextContent:
        """Provide fallback reasoning when primary reasoning fails."""
        console.print("[blue]FUNCTION CALL:[/blue] fallback_reasoning()")
        console.print(f"[blue]Step Description:[/blue] {step_description}")
        
        # Create an error panel with the step description
        console.print(Panel(
            f"[yellow]Fallback triggered:[/yellow]\n{step_description}",
            title="Fallback Reasoning",
            border_style="red"
        ))
        
        # Use the decision component to generate fallback reasoning
        from decision import Decision
        decision = Decision(self.memory)
        reasoning = decision.generate_fallback_reasoning(step_description)
        
        return TextContent(
            type="text",
            text=reasoning
        )
    
    def strings_to_chars_to_int(self, string: str) -> list:
        """Return the ASCII values of the characters in a word."""
        console.print("[blue]FUNCTION CALL:[/blue] strings_to_chars_to_int()")
        result = [ord(char) for char in string]
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def int_list_to_exponential_sum(self, int_list: list) -> float:
        """Return sum of exponentials of numbers in a list."""
        console.print("[blue]FUNCTION CALL:[/blue] int_list_to_exponential_sum()")
        result = sum(math.exp(x) for x in int_list)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    def fibonacci_numbers(self, n: int) -> list:
        """Return the first n Fibonacci Numbers."""
        console.print("[blue]FUNCTION CALL:[/blue] fibonacci_numbers()")
        if n < 0:
            raise ValueError("Number of Fibonacci numbers must be non-negative")
        result = [0, 1]
        for _ in range(2, n):
            result.append(result[-1] + result[-2])
        self.memory.add_to_history(f"fibonacci({n})", result)
        console.print(f"[green]Result:[/green] {result}")
        return result
    
    # def create_thumbnail(self, image_path: str) -> PILImage.Image:
    #     """Create a thumbnail from an image."""
    #     console.print("[blue]FUNCTION CALL:[/blue] create_thumbnail()")
    #     try:
    #         img = PILImage.open(image_path)
    #         img.thumbnail((100, 100))
    #         return img
    #     except Exception as e:
    #         raise ValueError(f"Error creating thumbnail: {str(e)}")
    
    # def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> dict:
    #     """Draw a rectangle in Paint from (x1,y1) to (x2,y2)."""
    #     console.print("[blue]FUNCTION CALL:[/blue] draw_rectangle()")
    #     try:
    #         # Get the Paint app from perceive component
    #         paint_app = self.perceive.paint_app
    #         if not paint_app:
    #             return {"status": "error", "message": "Paint is not open. Please call open_paint first."}
            
    #         # Get the Paint window
    #         paint_window = paint_app.window(class_name='MSPaintApp')
            
    #         # Get primary monitor width to adjust coordinates
    #         primary_width = win32gui.GetSystemMetrics(0)
            
    #         # Ensure Paint window is active
    #         if not paint_window.has_focus():
    #             paint_window.set_focus()
    #             time.sleep(0.2)
            
    #         # Click on the Rectangle tool using the correct coordinates for secondary screen
    #         paint_window.click_input(coords=(530, 82))
    #         time.sleep(0.2)
            
    #         # Get the canvas area
    #         canvas = paint_window.child_window(class_name='MSPaintView')
            
    #         # Draw rectangle - coordinates should already be relative to the Paint window
    #         # No need to add primary_width since we're clicking within the Paint window
    #         canvas.press_mouse_input(coords=(x1+2560, y1))
    #         canvas.move_mouse_input(coords=(x2+2560, y2))
    #         canvas.release_mouse_input(coords=(x2+2560, y2))
            
    #         return {"status": "success", "message": f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"}
    #     except Exception as e:
    #         return {"status": "error", "message": f"Error drawing rectangle: {str(e)}"}
    
    # def add_text_in_paint(self, text: str) -> dict:
    #     """Add text in Paint."""
    #     console.print("[blue]FUNCTION CALL:[/blue] add_text_in_paint()")
    #     try:
    #         # Get the Paint app from perceive component
    #         paint_app = self.perceive.paint_app
    #         if not paint_app:
    #             return {"status": "error", "message": "Paint is not open. Please call open_paint first."}
            
    #         # Get the Paint window
    #         paint_window = paint_app.window(class_name='MSPaintApp')
            
    #         # Ensure Paint window is active
    #         if not paint_window.has_focus():
    #             paint_window.set_focus()
    #             time.sleep(0.5)
            
    #         # Click on the Rectangle tool
    #         paint_window.click_input(coords=(528, 92))
    #         time.sleep(0.5)
            
    #         # Get the canvas area
    #         canvas = paint_window.child_window(class_name='MSPaintView')
            
    #         # Select text tool using keyboard shortcuts
    #         paint_window.type_keys('t')
    #         time.sleep(0.1)
    #         paint_window.type_keys('x')
    #         time.sleep(0.5)
            
    #         # Click where to start typing
    #         canvas.click_input(coords=(810, 533))
    #         time.sleep(0.5)
            
    #         # Type the text passed from client
    #         paint_window.type_keys(text)
    #         time.sleep(0.5)
            
    #         # Click to exit text mode
    #         canvas.click_input(coords=(1050, 800))
            
    #         return {"status": "success", "message": f"Text:'{text}' added successfully"}
    #     except Exception as e:
    #         return {"status": "error", "message": f"Error: {str(e)}"}
    
    # def open_paint(self) -> dict:
    #     """Open Microsoft Paint maximized on secondary monitor."""
    #     console.print("[blue]FUNCTION CALL:[/blue] open_paint()")
    #     try:
    #         # Use the perceive component to open Paint
    #         result = self.perceive.open_paint()
            
    #         # Update the paint app reference
    #         self.paint_app = self.perceive.paint_app
            
    #         # Store the paint state in memory
    #         self.memory.set_paint_state({"open": True, "timestamp": time.time()})
            
    #         return result
    #     except Exception as e:
    #         return {"status": "error", "message": f"Error opening Paint: {str(e)}"} 