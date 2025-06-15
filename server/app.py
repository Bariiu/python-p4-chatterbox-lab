from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_dict = [message.to_dict() for message in messages]
    return jsonify(messages_dict), 200

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201
    except KeyError:
        return jsonify({"errors": ["Missing body or username"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    return jsonify(message.to_dict()), 200

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        if 'body' in data:
            message.body = data['body']
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    try:
        db.session.delete(message)
        db.session.commit()
        return make_response('', 204)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555)