from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson.regex import Regex

app = Flask(__name__)
mongo = MongoClient("mongodb://localhost:27017/")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/top_users')
def top_users():
        pipeline = [
            {"$group": {"_id": "$user", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        top_users = list(mongo.BigData_tweets.tweets.aggregate(pipeline))
        return jsonify(users=top_users)
    
@app.route('/tweet_trends')
def tweet_trends():
    word_query = request.args.get('word', '').strip()
    regex = Regex(f".*{word_query}.*", "i") 
    pipeline = [
        {"$match": {"text": regex}},
        {"$addFields": {"dayOfWeek": {"$dayOfWeek": {"$dateFromString": {"dateString": "$date"}}}}},
        {"$group": {"_id": "$dayOfWeek", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    WordsperDay = list(mongo.BigData_tweets.tweets.aggregate(pipeline))
    return jsonify(WordsperDay=WordsperDay)
    

if __name__ == '__main__':
    app.run(debug=True)
