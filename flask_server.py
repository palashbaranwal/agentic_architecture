# flask_server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from perceive import Perceive

app = Flask(__name__)
CORS(app)  # Allow all origins for development

perceive = Perceive()

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    print("Received data:", data)  
    problem = data.get('problem', '')
    print("Problem:", problem)  
    result = perceive.parse_expression(problem)
    if result is None:
        return jsonify({'result': 'Invalid expression or error in calculation.'})
    return jsonify({'result': str(result)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)