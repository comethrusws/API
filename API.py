from flask import Flask, request, jsonify
from googlesearch import search
from functools import wraps
from ratelimit import limits, sleep_and_retry

app = Flask(__name__)

#rate-limits
@sleep_and_retry
@limits(calls=5, period=10)
def perform_search(query):
    return list(search(query, num=5, stop=5))

#API error ko lagi exception
class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.args.get('api_key')
        if api_key != 'your_api_key':
            raise APIError('Unauthorized', 401)
        return func(*args, **kwargs)
    return wrapper

@app.route('/api/search', methods=['GET'])
@authenticate
def search_google():
    query = request.args.get('query', '')

    if not query:
        raise APIError('Missing query parameter', 400)

    try:
        search_results = perform_search(query)
        return jsonify({'results': search_results}), 200
    except Exception as e:
        raise APIError(str(e), 500)

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'error': error.description})
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run(debug=True)
