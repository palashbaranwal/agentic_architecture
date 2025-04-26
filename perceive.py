from mcp.types import TextContent
from mcp import types
from typing import List, Dict, Any, Union
import math
import re
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import sys
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

# Configure logging
logging.basicConfig(
    filename='perceive.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Perceive')

console = Console()

class Perceive:
    """Component responsible for perceiving and understanding the environment."""
    
    def __init__(self):
        self.last_expression = None
        self.last_result = None
        self.error_patterns = {}
        logger.info("Perceive class initialized")
    
    def parse_expression(self, expression: str) -> Union[float, None]:
        """Parse and validate a mathematical expression"""
        try:
            # Remove any whitespace
            expression = expression.strip()
            
            # Basic validation
            if not expression:
                logger.warning("Empty expression provided")
                return None
                
            # Check for valid characters
            valid_chars = set('0123456789+-*/()^% .')
            if not all(c in valid_chars for c in expression):
                logger.warning(f"Invalid characters in expression: {expression}")
                return None
                
            # Check for balanced parentheses
            if expression.count('(') != expression.count(')'):
                logger.warning(f"Unbalanced parentheses in expression: {expression}")
                return None
                
            # Replace ^ with ** for Python power operator
            expression = expression.replace('^', '**')
            
            # Evaluate the expression
            result = eval(expression)
            
            # Store the last valid expression and result
            self.last_expression = expression
            self.last_result = result
            
            logger.info(f"Successfully parsed expression: {expression} = {result}")
            return float(result)
            
        except Exception as e:
            logger.error(f"Error parsing expression: {str(e)}")
            return None
    
    def verify_calculation(self, expression: str, expected_result: float) -> bool:
        """Verify if a calculation is correct"""
        try:
            actual_result = self.parse_expression(expression)
            if actual_result is None:
                logger.warning("Could not verify calculation due to invalid expression")
                return False
                
            # Compare with some tolerance for floating point
            is_correct = abs(actual_result - expected_result) < 1e-10
            logger.info(f"Verification result: {is_correct} (expected: {expected_result}, got: {actual_result})")
            return is_correct
            
        except Exception as e:
            logger.error(f"Error verifying calculation: {str(e)}")
            return False
    
    def check_consistency(self, expression: str, result: float) -> bool:
        """Check if a calculation is consistent with mathematical rules"""
        try:
            # Basic consistency checks
            if expression.count('(') != expression.count(')'):
                logger.warning("Unbalanced parentheses in consistency check")
                return False
                
            # Check division by zero
            if '/0' in expression.replace('/0.', ''):
                logger.warning("Division by zero detected in consistency check")
                return False
                
            # Check for valid mathematical operations
            valid_ops = set('+-*/^%')
            if not any(op in expression for op in valid_ops):
                logger.warning("No valid mathematical operations found in consistency check")
                return False
                
            # Verify the calculation
            is_consistent = self.verify_calculation(expression, result)
            logger.info(f"Consistency check result: {is_consistent}")
            return is_consistent
            
        except Exception as e:
            logger.error(f"Error checking consistency: {str(e)}")
            return False
    
    def show_reasoning(self, expression: str) -> str:
        """Show step-by-step reasoning for a calculation"""
        try:
            steps = []
            current = expression
            logger.info(f"Starting reasoning for expression: {expression}")
            
            # Handle parentheses first
            while '(' in current:
                start = current.rindex('(')
                end = current.index(')', start)
                sub_expr = current[start+1:end]
                result = str(eval(sub_expr))
                steps.append(f"Evaluate {sub_expr} = {result}")
                current = current[:start] + result + current[end+1:]
                logger.debug(f"Evaluated parentheses: {sub_expr} = {result}")
            
            # Handle exponents
            while '^' in current:
                current = current.replace('^', '**')
                logger.debug("Converted ^ to **")
            
            # Handle multiplication and division
            while '*' in current or '/' in current:
                if '*' in current and '/' in current:
                    op = '*' if current.index('*') < current.index('/') else '/'
                else:
                    op = '*' if '*' in current else '/'
                    
                idx = current.index(op)
                left = current[:idx].strip()
                right = current[idx+1:].strip()
                result = str(eval(left + op + right))
                steps.append(f"Evaluate {left} {op} {right} = {result}")
                current = current.replace(left + op + right, result)
                logger.debug(f"Evaluated {op} operation: {left} {op} {right} = {result}")
            
            # Handle addition and subtraction
            while '+' in current or '-' in current:
                if '+' in current and '-' in current:
                    op = '+' if current.index('+') < current.index('-') else '-'
                else:
                    op = '+' if '+' in current else '-'
                    
                idx = current.index(op)
                left = current[:idx].strip()
                right = current[idx+1:].strip()
                result = str(eval(left + op + right))
                steps.append(f"Evaluate {left} {op} {right} = {result}")
                current = current.replace(left + op + right, result)
                logger.debug(f"Evaluated {op} operation: {left} {op} {right} = {result}")
            
            logger.info("Completed reasoning steps")
            return "\n".join(steps)
            
        except Exception as e:
            logger.error(f"Error showing reasoning: {str(e)}")
            return "Unable to show reasoning"
    
    def parse_command(self, command: str) -> dict:
        """Parse a user command to determine the intended action."""
        command = command.lower().strip()
        logger.info(f"Parsing command: {command}")
        
        if 'calculate' in command or 'compute' in command or 'eval' in command:
            # Extract the expression
            expression = command.replace('calculate', '').replace('compute', '').replace('eval', '').strip()
            logger.info(f"Identified calculate action with expression: {expression}")
            return {'action': 'calculate', 'expression': expression}
        
        elif 'verify' in command or 'check' in command:
            # Extract the expression and expected result
            parts = command.replace('verify', '').replace('check', '').strip().split('=')
            if len(parts) == 2:
                logger.info(f"Identified verify action with expression: {parts[0].strip()} and expected: {parts[1].strip()}")
                return {'action': 'verify', 'expression': parts[0].strip(), 'expected': float(parts[1].strip())}
            else:
                logger.warning("Invalid verify command format")
                return {'action': 'error', 'message': 'Invalid verify command format'}
        
        elif 'reason' in command or 'steps' in command:
            # Extract the expression
            expression = command.replace('reason', '').replace('steps', '').strip()
            logger.info(f"Identified reason action with expression: {expression}")
            return {'action': 'reason', 'expression': expression}
        
        elif 'consistency' in command:
            # Extract the steps
            steps = command.replace('consistency', '').strip()
            logger.info(f"Identified consistency check with steps: {steps}")
            return {'action': 'check_consistency', 'steps': steps}
        
        else:
            # Default to calculating the expression
            logger.info(f"Defaulting to calculate action with expression: {command}")
            return {'action': 'calculate', 'expression': command} 