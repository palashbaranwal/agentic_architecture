from flask import Flask, request, jsonify
from flask_cors import CORS
from perceive import Perceive

app = Flask(__name__)
CORS(app)  # Allow all origins for development

perceive = Perceive()

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    problem = data.get('problem', '')
    gemini_key = data.get('gemini_key', '')

    # Pass gemini_key to your agent logic as needed
    # For example, you might set it as an attribute or pass it to a function
    # perceive.set_gemini_key(gemini_key)  # If you have such a method

    result = perceive.parse_expression(problem)
    if result is None:
        return jsonify({'result': 'Invalid expression or error in calculation.'})
    return jsonify({'result': str(result)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)