import jwt
import datetime
from flask import current_app as app
from time import time
from mongoengine import Document, StringField, IntField
import logging
logger = logging.getLogger()


class User(Document):
    allow_change = ["password"]
    username = StringField(required=True, max_length=200)
    password = StringField(required=True)
    privilege = IntField(required=False, default=0)

    def update_with_dict(self, user: dict):
        for key in user:
            if key in self.allow_change:
                self[key] = user[key]
        self.save()

    @staticmethod
    def login(username, password):
        users = User.objects(username=username, password=password)
        if users.count() == 0:
            logger.debug("Logging failed with username '{0},{1}'".format(
                username, password))
            return None
        elif users.count() == 1:
            user = users[0]
            user.token = (Auth.encode_auth_token(users[0].username, int(
                time()))).decode()
            return user
        else:
            try:
                raise UserError("Mutilple User found, please check database")
            except UserError as e:
                print(e)
            return None

    @staticmethod
    def get_user(username=None, uid=None):
        users = None
        if username is not None:
            users = User.objects(username=username)
        elif uid is not None:
            users = User.objects(id=uid)
        if users.count() > 0:
            return users[0]
        return None

    def get_dict(self):
        return {
            "username": self.username,
            "uid": str(self.id),
            "privilege": str(self.privilege)
        }

    @staticmethod
    def verify_auth_token(token):
        """
        Verify auth token and return owner of this token.
        Args:
            token (str): Input token

        Returns:
            user (User): Owner of this token.

        """
        playload = Auth.decode_auth_token(token)
        if playload == -1:
            return -1
        users = User.objects(username=playload['data']['username'])
        if len(users) > 0:
            return users[0]
        else:
            return None


class UserError(Exception):
    """ Error to raise while search users' information in database. 
    """
    pass


# Auth part for JWT auth
class Auth():
    @staticmethod
    def encode_auth_token(username, login_time) -> str:
        """ Get token from username and login time

        Args:
            login_time (int): timestamp 

        Raises:
            e: Exception

        Returns:
            str: token
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
                'iat': datetime.datetime.utcnow(),
                'data': {
                    'username': username,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload, app.config['SECRET_KEY'], algorithm='HS256')
        except Exception as e:
            raise e
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validate JWT
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token,
                app.config['SECRET_KEY'],
                options={'Verify_exp': False})
            if ('data' in payload and 'username' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return -2
        except jwt.InvalidTokenError:
            return -1
