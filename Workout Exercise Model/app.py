from flask import Flask, request, jsonify
from recommender import recommend_workout

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        result = recommend_workout(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def home():
    return "API is running. Use POST /recommend to get workout recommendations."
