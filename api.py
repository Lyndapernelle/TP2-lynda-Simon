from asyncio import sleep
from flask import Blueprint, jsonify, request
from time import sleep
from werkzeug.exceptions import HTTPException

import bd

bp_api = Blueprint("api", __name__)


@bp_api.errorhandler(HTTPException)
def gerer_erreur_http(e):
    return (
        jsonify({"code": e.code, "nom": e.name, "description": e.description}),
        e.code,
    )