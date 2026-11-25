
from flask import Blueprint, jsonify, request, abort, render_template, session, hashlib 
import random
from asyncio import sleep
from time import sleep
from werkzeug.exceptions import HTTPException
import re
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

@bp_api.route('/page_collection')
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
      
@bp_api.route('/liste_utilisateur')
def lister_utilisateur():

    courriel = request.args.get('courriel')
    if not courriel:
        return jsonify({
            "error": True,
            "msg_erreur_courriel": "Le courriel est obligatoire."
        }), 400
    if (len(courriel) < 3):
        return jsonify({
            "erreur": True,
            "msg_erreur_courriel" : "Le courriel doit au moins contenir 3 caractères."
        }), 400
    if 'courriel' in session != 'admin@garneau.ca':
        return jsonify({
            "error": True,
            "msg_erreur_courriel" : "Tu doit être admin pour accèder a cette recherche."
        }), 403
   
    with bd.creer_connexion() as conn:
        resultats = bd.trouver_utilisateur_avec_courriel(conn=conn,courriel=courriel)
        if not resultats:
            return jsonify({
                "erreur": True,
                "msg_erreur_courriel" : "Le courriel doit être existant."
            }), 401
        return jsonify({
            "erreur": False,
            "resultat": resultats
        }), 200

@bp_api.route('/creer-compte-rapide', methods=["POST", "GET"])
def ajout_compte_rapide():
    if request.method == "GET":
        return render_template("compte/creer-compte-rapide.jinja", titre="Ajout d'un compte admin")
    if request.method == "POST":
        x = random.randint(0, 1000000)
        courriel_regex = re.compile('^(admin){x}(garneau.ca)$')
        mdp = request.args.get("mot_de_passe")
        courriel = request.args.get("courriel")
        if not courriel_regex.match(courriel):
            return jsonify({
                "erreur": True,
                "msg_erreur_courriel" : "Le courriel n'est pas valide."
            })


        mdp_hash = mdp_hash(mdp)
        try:
            with bd.creer_connexion() as conn:
                bd.creer_compte(conn=conn, courriel=courriel, mdp_hash=mdp_hash)
                return jsonify({
                    "erreur": False,
                    "succes": "Le compte a été créer avec succès."
                })
        except Exception:
            return jsonify({
                "erreur": True,
                "message": "Erreur server"
            }), 500
        








def hasher_mdp(mdp_clair):
    return hashlib.sha512(mdp_clair.encode()).hexdigest()
