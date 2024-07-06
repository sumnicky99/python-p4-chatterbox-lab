# Import necessary modules from Flask and other libraries
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

# Import database and model configurations from the models module
from models import db, Message

# Initialize Flask app
app = Flask(__name__)

# Configure the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# Disable track modifications to suppress a warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Ensure the JSON output is not compacted
app.json.compact = False

# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

# Initialize database migration capabilities
migrate = Migrate(app, db)

# Bind the app to the database
db.init_app(app)

# Define the route for getting and posting messages
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    # Handle the GET request
    if request.method == 'GET':
        # Retrieve all messages, convert them to dictionaries, and order by creation date
        messages = [message.to_dict() for message in Message.query.order_by(Message.created_at.asc()).all()]
        return jsonify(messages), 200

    # Handle the POST request
    elif request.method == 'POST':
        # Create a new message using the provided JSON data
        new_message = Message(
            body=request.json['body'],
            username=request.json['username']
        )
        
        # Add the new message to the database session and commit the changes
        db.session.add(new_message)
        db.session.commit()
        
        # Return the newly created message as a JSON response
        return jsonify(new_message.to_dict()), 201

# Define the route for getting, updating, and deleting messages by ID
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    # Retrieve the message by its ID
    message = Message.query.get(id)
    
    # If the message doesn't exist, return a 404 error
    if not message:
        return jsonify({"message": "This record does not exist in our database. Please try again."}), 404
    
    # Handle the GET request to retrieve a specific message
    if request.method == 'GET':
        return jsonify(message.to_dict()), 200
    
    # Handle the PATCH request to update a specific message
    elif request.method == 'PATCH':
        # Update the message body if provided in the request JSON
        if 'body' in request.json:
            message.body = request.json['body']
        
        # Commit the changes to the database
        db.session.commit()
        return jsonify(message.to_dict()), 200
        
    # Handle the DELETE request to remove a specific message
    elif request.method == 'DELETE':
        # Delete the message from the database and commit the changes
        db.session.delete(message)
        db.session.commit()
        
        # Return a success message
        return jsonify({"delete_successful": True, "message": "Message deleted."}), 200

# Run the Flask app on port 5555
if __name__ == '__main__':
    app.run(port=5555)