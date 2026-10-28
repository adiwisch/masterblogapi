from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    title = data["title"]
    content = data["content"]
    missing_fields = []

    if not data or not data.get('title'):
        missing_fields.append('title')

    if not data or not data.get('content'):
        missing_fields.append('content')

    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'missing_fields': missing_fields
        }), 400

    new_id = max((post['id'] for post in POSTS), default=0) + 1

    new_post = {
        'id': new_id,
        'title': title,
        'content': content,
    }

    # add new post to existing ones
    POSTS.append(new_post)
    return jsonify(new_post), 201



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
