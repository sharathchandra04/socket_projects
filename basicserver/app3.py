from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple API endpoint (SPI-like)
@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World 3"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)