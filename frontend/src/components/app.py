
from flask import Flask, jsonify, request
from flask_cors import CORS
from pieChart import pieChart

app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})  # Adjust origins as needed

@app.route('/api/data', methods=['GET'])
def get_data():
    response = jsonify({'some': 'data'})
    return response

@app.route('/api/messages', methods=['POST'])
def post_data():
    data = request.form.getlist('data')  # Retrieve data from the request form
    chart_response = pieChart()

    if data:
     joined_string = ','.join(data)
     result_array = joined_string.split(',')
     returnValue = chart_response.illegalActivities(result_array)
     return returnValue
    
    else:
     response = jsonify({'message': 'Data received successfully'})
     return response


if __name__ == '__main__':
    app.run(debug=True)



