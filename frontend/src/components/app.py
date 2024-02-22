
# from flask import Flask, jsonify,request, Response
# from flask_cors import CORS
# from pieChart import pieChart
# import json

# app = Flask(__name__)
# CORS(app)

# @app.route('/api/data', methods=['GET'])
# def get_data():
#     response = jsonify({'some': 'data'})
#     return response

# @app.route('/api/messages', methods=['POST'])
# def post_data():
#     # data = request.json
#     # chart_response = pieChart()
#     # dataResponse = jsonify(data)
#     # #array  = json.loads(dataResponse)
#     # #returnValue = chart_response.textClassifier(array)
#     # message_array = [data[key] for key in sorted(data.keys())]
#     # print(message_array)
#     # returnValue = chart_response.textClassifier(message_array)
#     # response = jsonify({'message': 'Data received successfully'})
#     # # return response
#     # return returnValue


#     data = request.json
#     print(data)
#     chart_response = pieChart()
#     # No need to jsonify data
#     # message_array = [data[key] for key in sorted(data.keys())]
#     # Instead, you can directly use the data as a list
#     message_array = data
#     #print(message_array)
#     if(data != None):
#      returnValue = chart_response.illegalActivities(message_array)
#      return returnValue
    
#     response = jsonify({'message': 'Data received successfully'})
#     return response  # Return the response object

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, jsonify, request
from flask_cors import CORS
from pieChart import pieChart

app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
    response = jsonify({'some': 'data'})
    return response

@app.route('/api/messages', methods=['POST'])
def post_data():
    data = request.json
    print(data)
    chart_response = pieChart()
    
    if data is not None:
        message_array = data
        returnValue = chart_response.illegalActivities(message_array)
        return returnValue
    else:
        response = jsonify({'message': 'Data received successfully'})
        return response

if __name__ == '__main__':
    app.run(debug=True)



