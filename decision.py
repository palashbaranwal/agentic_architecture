from mcp.types import TextContent
from typing import List, Dict, Any, Tuple, Optional
import math
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

class Decision:
    """Component responsible for evaluating options and determining actions."""
    
    def __init__(self, memory):
        self.memory = memory
    
    def decide_operation(self, expression: str) -> Tuple[str, List[Any]]:
        """Decide which mathematical operation to perform based on the expression."""
        # Check if it's a basic operation
        if '+' in expression:
            parts = expression.split('+')
            return 'add', [int(p.strip()) for p in parts]
        elif '-' in expression:
            parts = expression.split('-')
            return 'subtract', [int(p.strip()) for p in parts]
        elif '*' in expression:
            parts = expression.split('*')
            return 'multiply', [int(p.strip()) for p in parts]
        elif '/' in expression:
            parts = expression.split('/')
            return 'divide', [int(p.strip()) for p in parts]
        elif '^' in expression:
            parts = expression.split('^')
            return 'power', [int(p.strip()) for p in parts]
        else:
            # Check for more complex operations
            if 'sqrt' in expression:
                num = re.search(r'sqrt\((\d+)\)', expression)
                if num:
                    return 'sqrt', [int(num.group(1))]
            
            if 'cbrt' in expression:
                num = re.search(r'cbrt\((\d+)\)', expression)
                if num:
                    return 'cbrt', [int(num.group(1))]
            
            if 'factorial' in expression or '!' in expression:
                num = re.search(r'factorial\((\d+)\)|(\d+)!', expression)
                if num:
                    return 'factorial', [int(num.group(1) or num.group(2))]
            
            if 'log' in expression:
                num = re.search(r'log\((\d+)\)', expression)
                if num:
                    return 'log', [int(num.group(1))]
            
            if 'sin' in expression:
                num = re.search(r'sin\((\d+)\)', expression)
                if num:
                    return 'sin', [int(num.group(1))]
            
            if 'cos' in expression:
                num = re.search(r'cos\((\d+)\)', expression)
                if num:
                    return 'cos', [int(num.group(1))]
            
            if 'tan' in expression:
                num = re.search(r'tan\((\d+)\)', expression)
                if num:
                    return 'tan', [int(num.group(1))]
            
            # Default to calculate for complex expressions
            return 'calculate', [expression]
    
    def verify_calculation(self, expression: str, expected: float) -> Tuple[bool, str]:
        """Verify if a calculation is correct."""
        try:
            actual = float(eval(expression))
            is_correct = abs(actual - float(expected)) < 1e-10
            
            if is_correct:
                return True, f"✓ Correct! {expression} = {expected}"
            else:
                return False, f"✗ Incorrect! {expression} should be {actual}, got {expected}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_consistency(self, steps: List[str]) -> Dict[str, Any]:
        """Check if calculation steps are consistent with each other."""
        issues = []
        warnings = []
        insights = []
        
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
        
        previous = None
        
        for i, step in enumerate(steps, 1):
            # Parse the step to get expression and result
            parts = step.split('=')
            if len(parts) != 2:
                issues.append(f"Step {i}: Invalid format")
                continue
                
            expression, result = parts[0].strip(), parts[1].strip()
            checks = []
            
            # Skip empty results
            if not result:
                issues.append(f"Step {i}: Empty result")
                checks.append("[red]✗ Empty result[/red]")
                table.add_row(
                    str(i),
                    expression,
                    result,
                    ", ".join(checks)
                )
                continue
            
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
                try:
                    ratio = abs(float(result) / float(previous[1]))
                    if ratio > 1000:
                        warnings.append(f"Step {i}: Large increase ({ratio:.2f}x)")
                        checks.append("[yellow]! Large magnitude increase[/yellow]")
                    elif ratio < 0.001:
                        warnings.append(f"Step {i}: Large decrease ({1/ratio:.2f}x)")
                        checks.append("[yellow]! Large magnitude decrease[/yellow]")
                except (ValueError, ZeroDivisionError):
                    warnings.append(f"Step {i}: Couldn't compare magnitudes")
                    checks.append("[yellow]! Magnitude comparison failed[/yellow]")
            
            # 4. Pattern Analysis
            operators = re.findall(r'[\+\-\*\/\(\)]', expression)
            if '(' in operators and ')' not in operators:
                warnings.append(f"Step {i}: Mismatched parentheses")
                checks.append("[red]✗ Invalid parentheses[/red]")
            
            # 5. Result Range Check
            try:
                if abs(float(result)) > 1e6:
                    warnings.append(f"Step {i}: Very large result")
                    checks.append("[yellow]! Large result[/yellow]")
                elif abs(float(result)) < 1e-6 and float(result) != 0:
                    warnings.append(f"Step {i}: Very small result")
                    checks.append("[yellow]! Small result[/yellow]")
            except ValueError:
                warnings.append(f"Step {i}: Couldn't check result range")
                checks.append("[yellow]! Range check failed[/yellow]")
            
            # Add row to table
            table.add_row(
                str(i),
                expression,
                result,
                ", ".join(checks)
            )
            
            # Store for next iteration
            previous = (expression, result)
        
        # Generate report
        report = {
            "issues": issues,
            "warnings": warnings,
            "insights": insights,
            "table": table
        }
        
        return report
    
    def generate_fallback_reasoning(self, step_description: str) -> str:
        """Generate fallback reasoning when primary reasoning fails."""
        # Check if we have seen this error before
        error_resolution = self.memory.get_error_resolution("reasoning", step_description)
        if error_resolution:
            return f"Based on previous experience: {error_resolution}"
        
        # Generate a generic fallback reasoning
        return f"Fallback reasoning for: {step_description}\n" + \
               "1. Check if the expression is well-formed\n" + \
               "2. Verify that all operations are valid\n" + \
               "3. Ensure all variables are defined\n" + \
               "4. Consider simplifying the expression"
    
    def decide_error_handling(self, error: Exception) -> str:
        """Decide how to handle an error."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Check if we have seen this error before
        resolution = self.memory.get_error_resolution(error_type, error_message)
        if resolution:
            return resolution
        
        # Default error handling based on error type
        if error_type == "ZeroDivisionError":
            return "Cannot divide by zero. Please check your denominator."
        elif error_type == "ValueError":
            return "Invalid value. Please check your input."
        elif error_type == "SyntaxError":
            return "Invalid syntax in expression. Please check your expression format."
        elif error_type == "NameError":
            return "Undefined variable. Please define all variables before using them."
        else:
            return f"An error occurred: {error_message}" 