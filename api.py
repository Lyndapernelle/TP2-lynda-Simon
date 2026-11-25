from asyncio import sleep
from flask import Blueprint, jsonify, request,session
from time import sleep
from werkzeug.exceptions import HTTPException

import math
import bd
import hashlib

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
      

@bp_api.route('/recherche-compte')
def rechercher_courriel():
    courriel = request.args.get('mot_cle',default='').strip()
    if(len(courriel)<3):
       return jsonify([])
    with bd.creer_connexion() as conn:
        comptes = bd.rechercher_utilisateur(conn=conn,courriel= courriel)
    sleep(0.5)
    return jsonify(comptes)

@bp_api.route('/creer-compte-rapide',methods=["POST","GET"])
def creer_rapide():
    if request.method == 'POST':
        utilisateur= None
        courriel = request.form.get('courriel',default='')
        mdp = request.form.get('mdp',default='')
        mdp_hash = hasher_mdp(mdp)
        with bd.creer_connexion() as conn:
            bd.creer_compte(conn=conn,courriel=courriel,mdp_hash=mdp_hash)
            utilisateur =  bd.trouver_utilisateur(conn=conn,courriel=courriel,mdp_hash=mdp_hash)
        sleep(0.5)
        return jsonify(utilisateur)

def hasher_mdp(mdp_clair):
    return hashlib.sha512(mdp_clair.encode()).hexdigest()

@bp_api.errorhandler(HTTPException)
def gerer_erreur_http(e):
    return (
        jsonify({"code": e.code, "nom": e.name, "description": e.description}),
        e.code,
    )