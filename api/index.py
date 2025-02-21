from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS globally

@app.route('/bfhl', methods=['GET', 'POST'])
def handle_bfhl():
    if request.method == 'GET':
        return jsonify({"operation_code": 1}), 200
    elif request.method == 'POST':
        data = request.json.get('data', [])
        is_valid = True
        numbers = []
        alphabets = []

        for item in data:
            if isinstance(item, str) and len(item) == 1 and item.isalpha():
                alphabets.append(item)
            else:
                try:
                    int(item)
                    numbers.append(item)
                except (ValueError, TypeError):
                    is_valid = False

        if not is_valid:
            return jsonify({
                "is_success": False,
                "user_id": "john_doe_17091999",
                "email": "john@xyz.com",
                "roll_number": "ABCD123",
                "numbers": [],
                "alphabets": [],
                "highest_alphabet": []
            }), 400

        highest_alphabet = []
        if alphabets:
            max_char = max(alphabets, key=lambda x: x.upper())
            highest_alphabet = [max_char]

        return jsonify({
            "is_success": True,
            "user_id": "john_doe_17091999",
            "email": "john@xyz.com",
            "roll_number": "ABCD123",
            "numbers": numbers,
            "alphabets": alphabets,
            "highest_alphabet": highest_alphabet
        }), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)  # Enable multithreading
