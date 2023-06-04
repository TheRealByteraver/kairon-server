# https://www.youtube.com/watch?v=PTZiDnuC86g&ab_channel=TraversyMedia
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin, logging
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logging.getLogger('flask_cors').level = logging.DEBUG
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# provide context thing for flask (?)
app.app_context().push()

# To create the database, do:
# pipenv shell
# python
# from app import app
# from app import db
# db.create_all()

# Init ma (marshmallow)
ma = Marshmallow(app)

# Product Class/Model: always create a class for each db model
class Token(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    active = db.Column(db.Boolean, default=True)

    # 'self' is the equivalent of 'this' in javascript
    # __init__ is the class constructor
    def __init__(self, token, active):
        self.id = token
        self.active = active

# Product Schema
class TokenSchema(ma.Schema):
    # fields that we are allowed to show
    class Meta:
        model = Token
        fields = ('id', 'active')
        
# Init Schema
token_schema = TokenSchema()
tokens_schema = TokenSchema(many=True)

@app.route('/', methods=['GET'])
@cross_origin()
def get():
    return render_template('welcome.html')

# Create a token
@app.route('/token', methods=['POST'])
@cross_origin()
def add_token():
    id = request.json['id']
    active = True
    new_token = Token(id, active)
    try:
        db.session.add(new_token)
        db.session.commit()
        return token_schema.jsonify(new_token)
    except:
        return jsonify({ "error": "unable to add token '" + id + "', make sure you don't try to add the token twice."})

# Get all tokens
@app.route('/token', methods=['GET'])
@cross_origin()
def get_tokens():
    all_tokens = Token.query.all()
    result = tokens_schema.dump(all_tokens)
    return jsonify(result)

# Get a single token
@app.route('/token/<id>', methods=['GET'])
@cross_origin()
def get_token(id):
    token = Token.query.get(id)
    if(token):
        return token_schema.jsonify(token)
    else:
        return jsonify({ "error": "could not find token '" + id + "'"})

# Update a single token
@app.route('/token/<id>', methods=['PUT'])
@cross_origin()
def update_token(id):
    token = Token.query.get(id)
    if(token):
        token.active = request.json['active']
        db.session.commit()
        return token_schema.jsonify(token)
    else:
        return jsonify({ "error": "could not find token '" + id + "'"})

# Delete a single token
@app.route('/token/<id>', methods=['DELETE'])
@cross_origin()
def delete_token(id):
    token = Token.query.get(id)
    if(token):
        db.session.delete(token)
        db.session.commit()
        return token_schema.jsonify(token)
    else:
        return jsonify({ "error": "could not find token '" + id + "'"})
    
# Run server
if __name__ == '__main__':
    app.run(debug=True)
