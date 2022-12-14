from email import message
from flask_restful import Resource, reqparse, fields
from models.user import UserModel
from utils.file_handler import save_logo, delete_logo
import bcrypt
import werkzeug
import uuid
import os


class Users(Resource):
    def get(self):
        return {"users": [user.json() for user in UserModel.find_all()]}


class UserRegister(Resource):
    # headers = {"Content-Type": "application/json; charset=utf-8"}

    parser = reqparse.RequestParser()
    parser.add_argument('company_name',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('logo',
                        type=str,
                        help="This field cannot be blank.")
    parser.add_argument('email',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank.")
    parser.add_argument('logo',
                        type=werkzeug.datastructures.FileStorage, location='files',
                        required=False)

    def post(self):
        data = UserRegister.parser.parse_args()  # user register data
        
        file_name = f"{uuid.uuid4().hex}.png"

        if data['logo']:
            # return {"image" : data['logo'].filename} , 
            save_logo(data['logo'], file_name)
            data['logo'] = file_name

        # hashing password before save_to_db
        data['password'] = bcrypt.hashpw(
            data['password'].encode('utf8'), bcrypt.gensalt())

        is_exists = UserModel.check_if_user_exists(data)
        if is_exists:
            delete_logo(file_name)
            return {"message": "This user is already exists"}, 400

        user = UserModel(**data)
        try:
            user.save_to_db()
        except:
            return {"message": "An error occurred while creating the user."}, 500

        return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json()
        return {"message": "User not found."}, 404

    @classmethod
    def put(cls, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('company_name',
                            type=str,
                            required=True,
                            help="This field cannot be blank.")
        parser.add_argument('email',
                            type=str,
                            required=True,
                            help="This field cannot be blank.")
        parser.add_argument('logo',
                            type=werkzeug.datastructures.FileStorage, location='files',
                            required=False)
        data = parser.parse_args()

        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": "User not found."}, 404
        
        file_name = f"{uuid.uuid4().hex}.png"

        if data['logo']:

            if user.logo:
                delete_logo(user.logo)

            save_logo(data['logo'], file_name)
            user.logo = file_name
        

        user.company_name = data['company_name']
        user.email = data['email']

        try:
            user.save_to_db()
        except:
            return {"message": "Duplicate data. Please change it."}, 409

        return user.json(), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404
        try:
            user.delete_from_db()
            delete_logo(user.logo)
        except:
            return {"message": "An error occurred while deleting the user."}, 500

        return {"message": "User Deleted successfully."}, 201


class ChangePassword(Resource):
    @classmethod
    def put(cls, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('old_password',
                            type=str,
                            required=True,
                            help="This field cannot be blank.")
        parser.add_argument('new_password',
                            type=str,
                            required=True,
                            help="This field cannot be blank.")
        parser.add_argument('confirm_password',
                            type=str,
                            required=True,
                            help="This field cannot be blank.")
        data = parser.parse_args()

        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": "User not found."}, 404

        is_valid_password = bcrypt.checkpw(
            data['old_password'].encode('utf8'), user.password.encode('utf8'))

        if not is_valid_password:
            return {"message": "Old password is invalid!"}, 403

        if data['new_password'] != data['confirm_password']:
            return {"message": "Confirm password doesn't match new password!"}, 401

        # hashing password before save_to_db
        data['new_password'] = bcrypt.hashpw(
            data['new_password'].encode('utf8'), bcrypt.gensalt())

        # set password to new hashed password
        user.password = data['new_password']

        try:
            user.save_to_db()
        except:
            return {"message": "An error occurred while updating the password."}, 500

        return user.json(), 200


class CreateStaticUser(Resource):

    def get(self):
        data = {
            "company_name": "youssefwael",
            # 'logo': "",
            'email': 'youssefwael397@gmail.com',
            "password": "12345678"
        }
        print(data)
        # check_if_user_exists
        is_exists = UserModel.check_if_user_exists(data)
        if is_exists:
            return {"message": "A user with that company_name already exists"}, 400
        # if not => create new user
        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201
