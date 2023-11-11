from errors import HttpError
from flask import Response, request
from models import Session
from tools import get_json_response, handle_error
from views import LoginView, AdvtView, UserView

from app import get_app

JSON_METHODS = frozenset({"POST", "PUT", "PATCH"})

app = get_app()

@app.errorhandler(404)
def not_found(err):
    return get_json_response({"description": "url not found"}, 404)


@app.errorhandler(500)
def unexpected(err):
    msg = {"description": "unexpected error"}
    if app.debug:
        msg["error"] = str(err)
        msg["traceback"] = err.__traceback__
    return get_json_response(msg, 500)


@app.before_request
def before_requests():
    request.session = Session()

    if request.method in JSON_METHODS and not request.is_json:
        raise HttpError(400, "json format expected")


@app.after_request
def after_requests(response: Response):
    request.session.close()
    return response

user_view = UserView.as_view("user")
advt_view = AdvtView.as_view("advt")

app.add_url_rule(
    "/user", view_func=user_view, methods=["GET", "POST", "PATCH", "DELETE"]
)

app.add_url_rule("/login", view_func=LoginView.as_view("login"), methods=["POST"])

app.add_url_rule("/advertisement", view_func=advt_view, methods=["POST", "GET"])
app.add_url_rule(
    "/advertisement/<int:advt_id>", view_func=advt_view, methods=["GET", "PATCH", "DELETE"]
)

app.register_error_handler(HttpError, handle_error)

if __name__ == "__main__":
    app.run(debug=True)

