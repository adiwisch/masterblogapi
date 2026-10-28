"""Backend app for the Masterblog API project"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Andre Diwischs Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """get all blog posts, can be sorted by 'title' or 'content'."""
    # check for sorting parameters
    sort = request.args.get('sort')
    if sort:
        if sort not in ["title", "content"]:
            return jsonify({
                "message": "Sorting only supported for 'title' and 'content'."
            }), 400
        direction = request.args.get('direction')
        if direction:
            if direction not in ["asc", "desc"]:
                return jsonify({
                    "message": "Direction can only be 'asc' or 'desc'."
                }), 400
        else:
            direction = "asc"
        sorted_posts = sorted(
            POSTS,
            key=lambda post: post[sort].lower(),
            reverse=direction == "desc"
        )
        return jsonify(sorted_posts)

    return jsonify(POSTS)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """search for blog posts that contain desired stuff in title or content."""
    title = request.args.get('title', '').lower()
    content = request.args.get('content', '').lower()

    results = []

    for post in POSTS:
        title_matches = title and title in post['title'].lower()
        content_matches = content and content in post['content'].lower()

        if (not title or title_matches) and (not content or content_matches):
            results.append(post)

    return jsonify(results)



@app.route('/api/posts', methods=['POST'])
def add_post():
    """add a new blog post"""
    data = request.get_json()

    datacheck = check_post_contents(data)

    if datacheck != "OK":
        return datacheck

    new_id = max((post['id'] for post in POSTS), default=0) + 1

    new_post = {
        'id': new_id,
        'title': data.get('title'),
        'content': data.get('content'),
    }

    # add new post to existing ones
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """delete post with id"""
    # look for post with specified ID
    post_to_delete = next(
        (post for post in POSTS if post['id'] == post_id),
        None
    )
    if post_to_delete is None:
        # no post found: return error message
        return jsonify({
            "message": f"No post with id {post_id} found."
        }), 404
    # post found: remove post from all posts
    POSTS.remove(post_to_delete)
    # show success message
    return jsonify({
        "message": f"Post with id {post_id} has been deleted successfully."
    }), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update(post_id):
    """Update an existing blog post or display the form to do so."""
    # Get the blog post
    post = get_post_by_id(post_id)
    data = request.get_json()

    # return error if none found
    if post is None:
        return jsonify({
            "message": f"No post with id {post_id} found."
        }), 404

    # Update the selected post
    for blog_post in POSTS:
        if blog_post['id'] == post_id:
            if data.get('title') is not None:
                blog_post['title'] = data.get('title')
            if data.get('content') is not None:
                blog_post['content'] = data.get('content')
            break

    return jsonify({
        "message": f"Post with id {post_id} has been updated successfully."
    }), 200


def get_post_by_id(post_id):
    """Return a blog post by its ID - None if no post was found with that ID."""

    return next(
        (post for post in POSTS if post['id'] == post_id),
        None
    )

def check_post_contents(data):
    """check data for required fields"""

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
    return "OK"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
