from flask import Blueprint, jsonify, request, abort, render_template, session
from werkzeug.exceptions import HTTPException

import bd

bp_api = Blueprint("api", __name__)

@bp_api.errorhandler(HTTPException)
def gerer_erreur_http(e):
    return (
        jsonify({"code": e.code, "nom": e.name, "description": e.description}),
        e.code,
    )

@bp_api.route('/page_collection', methods=['GET'])
def rechercheCollection():
    nom_carte = request.args.get('nom_carte')
    courriel_utilisateur = session.get('courriel')
    if not nom_carte:
        return jsonify({
            "error": True,
            "msg_erreur_carte": "Le nom de la carte est obligatoire."
        }), 400
    with bd.creer_connexion() as conn:
        resultats = bd.collection_recherche(conn=conn, nom_carte=nom_carte, courriel_utilisateur=courriel_utilisateur)       
        if not resultats:
            return jsonify({
                "error": True,
                "msg_erreur_carte": "Le nom de la carte doit être existant."
            }), 400 
        return jsonify({
            "error": False,
            "resultat": resultats
        }), 200
      


