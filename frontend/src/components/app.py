
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

@app.route('/api/argumentativeClassifier', methods=['POST'])
def post_argumentative():
    data = request.form.getlist('data')  # Retrieve data from the request form
    chart_response = pieChart()

    if data:
     joined_string = ','.join(data)
     result_array = joined_string.split(',')
     returnValue = chart_response.argumentativeNature(result_array)
     return returnValue
    
    else:
     response = jsonify({'message': 'Data received successfully'})
     return response
    
@app.route('/api/strictKeyword', methods=['POST'])
def post_strictKeyword():
    data = request.form.getlist('data') 
    keyword = request.form.getlist('keyword') 
    chart_response = pieChart()
    
    if data and keyword:
        joined_string = ','.join(data)
        result_array = joined_string.split(',')
        returnValue = chart_response.strictKeywordSearch(keyword[0], result_array)
        return returnValue
    else:
        response = jsonify({'message': 'Incomplete data received'})
        return response
    
@app.route('/api/relatedKeyword', methods=['POST'])
def post_relatedKeyword():
    # data = request.form.getlist('data') 
    # keyword = request.form.getlist('keyword') 
    # chart_response = pieChart()
    
    # if data and keyword:
    #     joined_string = ','.join(data)
    #     result_array = joined_string.split(',')
    #     returnValue = chart_response.related_keyword_search(result_array, keyword[0])
    #     return returnValue
    # else:
    #     response = jsonify({'message': 'Incomplete data received'})
    #     return response
    data = request.form.getlist('data') 
    keyword = request.form.getlist('keyword') 
    chart_response = pieChart()
    
    if data and keyword:
        joined_string = ','.join(data)
        result_array = joined_string.split(',')
       
        synonyms, chart_data = chart_response.related_keyword_search(result_array, keyword[0])
        print(synonyms)
        print(chart_data)
        
        # Check if both synonyms and chart data are not None
        if synonyms is not None and chart_data is not None:
            response_data = {
                'synonyms': synonyms,
                'chart_data': chart_data
            }
            return (response_data)
        else:
            response = jsonify({'message': 'No data found'})
            return response
    else:
        response = jsonify({'message': 'Incomplete data received'})
        return response

    

# @app.route('/api/getSynonyms', methods=['POST'])
# def post_getsynonyms():
#     keyword = request.form.getlist('keyword') 
#     chart_response = pieChart()
#     data = request.form.getlist('data') 
    
#     if keyword:
#         # returnValue = chart_response.get_synonyms(keyword[0])
#         # print(returnValue)
#         # joined_string = ','.join(data)
#         # result_array = joined_string.split(',')
#         # returnValue = chart_response.related_keyword_search(result_array, keyword[0])
#         # returnValue = chart_response.syn
#         returnValue = keyword[0]
#         return returnValue
#     else:
#         response = jsonify({'message': 'Incomplete data received'})
#         return response


if __name__ == '__main__':
    app.run(debug=True)



