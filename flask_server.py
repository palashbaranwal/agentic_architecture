from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import tempfile
import json
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from rich.console import Console
import sys
import threading
import time

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

console = Console()

async def process_math_problem(gemini_api_key, problem):
    """Process a math problem using the MathAgent framework"""
    try:
        # Configure Gemini with the provided API key
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        client = genai.Client(api_key=gemini_api_key)
        
        # Create a temporary .env file with the API key
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as temp_env:
            temp_env.write(f"GEMINI_API_KEY={gemini_api_key}\n")
            temp_env_path = temp_env.name
        
        # Set up server parameters to run the math tools
        server_params = StdioServerParameters(
            command="python",
            args=["math_tools.py"]
        )
        
        # Store results from the calculation
        calculation_results = []
        final_answer = None
        
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
                        FINAL_ANSWER: [answer]"""

                prompt = f"{system_prompt}\n\nSolve this problem step by step: {problem}"
                conversation_history = []
                
                # Maximum iterations to prevent infinite loops
                max_iterations = 30
                iterations = 0
                
                while iterations < max_iterations:
                    iterations += 1
                    
                    response = await generate_with_timeout(client, prompt)
                    if not response or not response.text:
                        break

                    result = response.text.strip()
                    calculation_results.append({"role": "assistant", "content": result})
                    
                    if result.startswith("FUNCTION_CALL:"):
                        # Extract and process function calls
                        try:
                            is_valid, parsed_json, validation_message = validate_json(result)
                            
                            if parsed_json:
                                func_name = parsed_json["name"]
                                args = parsed_json["args"]
                                
                                if func_name == "show_reasoning":
                                    steps = args.get("steps", [])
                                    await session.call_tool("show_reasoning", arguments={"steps": steps})
                                    prompt += f"\nUser: Next step?"
                                    calculation_results.append({"role": "user", "content": "Next step?"})
                                    
                                elif func_name == "calculate":
                                    expression = args.get("expression", "")
                                    calc_result = await session.call_tool("calculate", arguments={"expression": expression})
                                    
                                    if calc_result.content:
                                        value = calc_result.content[0].text
                                        prompt += f"\nUser: Result is {value}. Let's verify this step."
                                        calculation_results.append({"role": "user", "content": f"Result is {value}. Let's verify this step."})
                                        conversation_history.append((expression, float(value)))
                                    else:
                                        error_msg = "No calculation result returned"
                                        prompt += f"\nUser: Error occurred. Fallback triggered. Please reconsider this step or try an alternative approach."
                                        calculation_results.append({"role": "user", "content": f"Error: {error_msg}"})
                                        
                                elif func_name == "verify":
                                    expression = args.get("expression", "")
                                    expected = float(args.get("expected", 0))
                                    await session.call_tool("verify", arguments={
                                        "expression": expression,
                                        "expected": expected
                                    })
                                    
                                    prompt += f"\nUser: Verification completed. Next step?"
                                    calculation_results.append({"role": "user", "content": "Verification completed. Next step?"})
                                    
                                elif func_name == "fallback_reasoning":
                                    step_description = args.get("step_description", "")
                                    await session.call_tool("fallback_reasoning", arguments={
                                        "step_description": step_description
                                    })
                                    prompt += "\nUser: Fallback processed. Please proceed with an alternative approach."
                                    calculation_results.append({"role": "user", "content": "Fallback processed. Please proceed with an alternative approach."})
                            
                        except Exception as e:
                            error_msg = str(e)
                            prompt += f"\nUser: Error occurred: {error_msg}. Please try an alternative approach."
                            calculation_results.append({"role": "user", "content": f"Error: {error_msg}"})

                    elif result.startswith("FINAL_ANSWER:"):
                        try:
                            final_answer = result.split("[")[1].split("]")[0]
                        except:
                            final_answer = "Could not extract final answer"
                        break
                    
                    prompt += f"\nAssistant: {result}"
                
        # Clean up temporary env file
        if os.path.exists(temp_env_path):
            os.unlink(temp_env_path)
            
        return {
            "success": True,
            "conversation": calculation_results,
            "final_answer": final_answer
        }
            
    except Exception as e:
        console.print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

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
        console.print(f"Error: {e}")
        return None

def validate_json(function_call: str):
    """
    Validates the JSON structure in a function call string.
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

@app.route('/api/solve', methods=['POST'])
def solve_problem():
    try:
        # Get data from request
        data = request.json
        gemini_api_key = data.get('api_key')
        problem = data.get('problem')
        
        # Validate inputs
        if not gemini_api_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key is required'
            }), 400
            
        if not problem:
            return jsonify({
                'success': False,
                'error': 'Problem is required'
            }), 400
        
        # Process the problem asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_math_problem(gemini_api_key, problem))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'Math Agent API'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)