from flask import Flask, render_template, request
import redis
import random
from flask import jsonify
import time


app = Flask(__name__)
redis_db = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)


@app.route("/")
def index():
    emojis = ["😀", "😂", "🤣", "😊", "😍", "🥰", "😎", "🤩", "🥳", "😜"]

    if not redis_db.exists("emojis"):
        redis_db.rpush("emojis", *emojis)

    random_index = random.randint(0, redis_db.llen("emojis") - 1)
    emoji = redis_db.lindex("emojis", random_index)

    return render_template("index.html", emoji=emoji)


# This is all for Beanstalk deployment
@app.route("/health")
def health():
    return "OK", 200


@app.route("/emojis")
def show_emojis():
    # Check if the Redis list is empty
    if redis_db.llen("emojis") == 0:
        # List of sample emojis to add
        sample_emojis = ["😀", "😂", "🙌", "💖", "🚀", "🌍", "👍", "🐱‍👓"]
        # Add each emoji to the Redis list
        for emoji in sample_emojis:
            redis_db.rpush("emojis", emoji)

    # Get the total number of emojis stored in Redis
    total_emojis = redis_db.llen("emojis")

    # Retrieve all emojis from Redis
    emojis = [redis_db.lindex("emojis", i) for i in range(total_emojis)]

    # Return a JSON response with all emojis
    return jsonify({"emojis": emojis})
# Create (Add) Endpoint
@app.route("/emojisr", methods=["POST"])
def create_emoji():
    data = request.get_json()
    emoji = data.get("emoji")

    if not emoji:
        return jsonify({"message": "Emoji is required"}), 400

    redis_db.rpush("emojis", emoji)
    return jsonify({"message": "Emoji added successfully"}), 201

# Read (Get All) Endpoint
@app.route("/emojisr", methods=["GET"])
def get_all_emojis():
    emojis = redis_db.lrange("emojis", 0, -1)
    return jsonify({"emojis": emojis})

# Update (Edit) Endpoint
@app.route("/emojisr/<int:index>", methods=["PUT"])
def update_emoji(index):
    data = request.get_json()
    emoji = data.get("emoji")

    if not emoji:
        return jsonify({"message": "Emoji is required"}), 400

    emojis_count = redis_db.llen("emojis")
    
    if index < 0 or index >= emojis_count:
        return jsonify({"message": "Invalid index"}), 400

    redis_db.lset("emojis", index, emoji)
    return jsonify({"message": "Emoji updated successfully"})

# Delete Endpoint
@app.route("/emojisr/<int:index>", methods=["DELETE"])
def delete_emoji(index):
    emojis_count = redis_db.llen("emojis")

    if index < 0 or index >= emojis_count:
        return jsonify({"message": "Invalid index"}), 400

    redis_db.lpop("emojis", index)
    return jsonify({"message": "Emoji deleted successfully"})


# @app.route("/hello")
# def check():
#     random_index = random.randint(0, redis_db.llen("emojis") - 1)
#     emoji = redis_db.lindex("emojis", random_index)

#     return render_template("hello.html", emoji=emoji)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
