from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api
from config import mysql_uri
from db import db
from models.user import UserModel
from models.member import MemberModel
from resources.member import CreateMember, Member, Members, MemberUser
from resources.user import UserRegister, Users, User, ChangePassword, CreateStaticUser
from resources.helloWorld import HelloWorld

app = Flask(__name__, static_url_path='/static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.before_first_request
def create_tables():
    db.init_app(app)
    db.create_all()

# api routes
api.add_resource(HelloWorld, '/') # base api url http://localhost:5000/
# Users
api.add_resource(CreateStaticUser, '/api/static/user/create') # for test
api.add_resource(UserRegister, '/api/register')
api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:user_id>')
api.add_resource(ChangePassword, '/api/changePassword/<int:user_id>')
# Members
api.add_resource(CreateMember, '/api/members/create')
api.add_resource(Members, '/api/members')
api.add_resource(Member, '/api/members/<int:member_id>')
# Members by user_id for test before token
api.add_resource(MemberUser, '/api/members/user/<int:user_id>')




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
