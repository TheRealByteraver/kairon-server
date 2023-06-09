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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

    # 'self' is the equivalent of 'this' in javascript
    # __init__ is the class constructor
    def __init__(self, token, active):
        self.name = token
        self.active = active

# Product Schema
class TokenSchema(ma.Schema):
    # fields that we are allowed to show
    class Meta:
        model = Token
        fields = ('id', 'name', 'active')
        
# Init Schema
token_schema = TokenSchema()
tokens_schema = TokenSchema(many=True)

# -----------------------------------------------------------------------------
# ------------------------------- ### Routes ### ------------------------------
# -----------------------------------------------------------------------------

@app.route('/', methods=['GET'])
@cross_origin()
def get():
    return render_template('welcome.html')

# Create a token
@app.route('/tokens', methods=['POST'])
@cross_origin()
def add_token():
    name = request.json['name']
    active = True
    new_token = Token(name, active)
    try:
        db.session.add(new_token)
        db.session.commit()
        return token_schema.jsonify(new_token)
    except:
        try:
            # check if the token already exist as an inactive token.
            # if so, reactivate it
            db.session.rollback() # this is necessary because of the previous exception
            inactive_token = Token.query.filter(Token.name == name).first()
            inactive_token.active = True
            db.session.commit()
            return token_schema.jsonify(inactive_token)
        except Exception as e:
            print("exception on reactivating token:", e)
            return jsonify({"error": "unable to add/reactivate token '" + name + "', make sure you don't try to add the token twice."})

# Get all tokens
@app.route('/tokens', methods=['GET'])
@cross_origin()
def get_tokens():
    query = request.args.get('query')
    if query == "inactive":
        active_tokens = Token.query.filter(Token.active == 0).all()
    else:
        active_tokens = Token.query.filter(Token.active == 1).all()
    result = tokens_schema.dump(active_tokens)
    return jsonify(result)

# Get a single token
@app.route('/tokens/<id>', methods=['GET'])
@cross_origin()
def get_token(id):
    token = Token.query.get(id)
    if(token):
        return token_schema.jsonify(token)
    else:
        return jsonify({ "error": "could not find token with id " + id})

# Update a single token
@app.route('/tokens/<id>', methods=['PATCH'])
@cross_origin()
def update_token(id):
    token = Token.query.get(id)
    if(token):
        token.active = request.json['active']
        db.session.commit()
        return token_schema.jsonify(token)
    else:
        return jsonify({ "error": "could not find token with id" + id})

# Run server
if __name__ == '__main__':
    app.run(debug=True)
