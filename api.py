from asyncio import sleep
from flask import Blueprint, jsonify, request,session
from time import sleep
from werkzeug.exceptions import HTTPException

import bd

bp_api = Blueprint("api", __name__)

@bp_api.route('/recherche')
def rechercher():
    peut_faire_offre = False
    nom_pokemon = request.args.get('nom_pokemon',default='').strip()
    if(len(nom_pokemon)<2):
       return jsonify([])
    with bd.creer_connexion() as conn:
        if('courriel' in session and session["courriel"] != 'invite@garneau.ca'):
            peut_faire_offre = True
            pokemons = bd.rechercher_nom(conn=conn, pNom=nom_pokemon,id_collectionneur=session['id'])
        else:
            pokemons = bd.rechercher_nom(conn=conn, pNom=nom_pokemon,id_collectionneur=0)
    return jsonify({"pokemon":pokemons,
                    "peut_faire_offre":peut_faire_offre})

@bp_api.errorhandler(HTTPException)
def gerer_erreur_http(e):
    return (
        jsonify({"code": e.code, "nom": e.name, "description": e.description}),
        e.code,
    )