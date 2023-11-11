import flask
from flask.views import MethodView
from sqlalchemy.orm import Session
from flask import jsonify, request
from models import Advt, Token, User
from auth import check_owner, check_password, check_token, hash_password
from tools import validate
from schema import CreateAdvt, CreateUser, Login, PatchUser
from crud import add_item, create_item, delete_item, get_item_by_id, update_item
from errors import HttpError

class BaseView(MethodView):
    @property
    def session(self) -> Session:
        return request.session

    @property
    def token(self) -> Token:
        return request.token

    @property
    def user(self) -> User:
        return request.token.user

class UserView(BaseView):
    @check_token
    def get(self):
        return jsonify(self.user.dict)

    def post(self):
        payload = validate(CreateUser, request.json)
        payload["password"] = hash_password(payload["password"])
        user = create_item(User, payload, self.session)
        return jsonify({"id": user.id})

    @check_token
    def patch(self):
        payload = validate(PatchUser, request.json)
        user = update_item(self.token.user, payload, self.session)
        return jsonify({"id": user.id})

    @check_token
    def delete(self):
        delete_item(self.token.user, self.session)
        return jsonify({"status": "ok"})

class LoginView(BaseView):
    def post(self):
        payload = validate(Login, request.json)
        user = self.session.query(User).filter_by(name=payload["name"]).first()
        if user is None:
            raise HttpError(404, "user not found")
        if check_password(user.password, payload["password"]):
            token = create_item(Token, {"user_id": user.id}, self.session)
            add_item(token, self.session)
            return jsonify({"token": token.token})
        raise HttpError(401, "invalid password")

class AdvtView(BaseView):
    @check_token
    def get(self, advt_id: int = None):
        if advt_id is None:
            return jsonify([advt.dict for advt in self.user.advts])
        advt = get_item_by_id(Advt, advt_id, self.session)
        check_owner(advt, self.token.user_id)
        return jsonify(advt.dict)

    @check_token
    def post(self):
        payload = validate(CreateAdvt, request.json)
        payload['user_id'] = self.token.user_id
        advt = create_item(Advt, payload, self.session)
        # advt = create_item(
        #     Advt, dict(owner_id=self.token.user_id, **payload), self.session
        # )
        return jsonify({"id": advt.id})

    # @check_token
    # def patch(self, todo_id: int):
    #     payload = validate(UpdateTodo, request.json)
    #     if "done" in payload:
    #         payload["finish_time"] = func.now()
    #     todo = get_item_by_id(Todo, todo_id, self.session)
    #     check_owner(todo, self.token.user_id)
    #     todo = update_item(todo, payload, self.session)
    #     return jsonify({"id": todo.id})

    @check_token
    def delete(self, advt_id: int):
        advt = get_item_by_id(Advt, advt_id, self.session)
        check_owner(advt, self.token.user_id)
        delete_item(advt, self.session)
        return jsonify({"status": "ok"})
