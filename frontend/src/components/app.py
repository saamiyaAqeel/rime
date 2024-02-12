
from flask import Flask, jsonify,request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
    response = jsonify({'some': 'data'})
    return response


@app.route('/api/messages', methods=['POST'])
def post_data():
    response = jsonify({'message': 'Data received successfully'})
    return response

if __name__ == '__main__':
    app.run(debug=True)


