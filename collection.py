"""
Exercice de page de détails
"""

from flask import Flask, render_template, request, redirect, abort, Blueprint
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import bd
import re
import html
from config import Config
from bulletin import bp_inscription_bulletin

bp_collection= Blueprint('collection', __name__)

bp_collection.register_blueprint(bp_inscription_bulletin, url_prefix="inscription")



@bp_collection.route("/recherche",methods=["GET"])
def recherche():
    pNom = request.args.get('nom_pokemon', default='').strip()
    pNumero = request.args.get('numero',type=int)
    pSuperType = request.args.get('supertype', default='').strip()
    pRarete = request.args.get('rarete',default='').strip() # Ces paramêtres ne sont pas obligatoires

    if not valide_supertype(pSuperType):
        abort(400," Paramètre 'superType' invalide")

    caracteres_interdits = re.compile('<(.*)>.*?|<(.*) />')

    if caracteres_interdits.match(pNom) :
        abort(400," Paramètre 'nom_pokemon' invalide")
    if caracteres_interdits.match(pRarete) :
        abort(400," Paramètre 'rarete' invalide")

    with bd.creer_connexion() as conn:
       resultat = bd.rechercher(conn=conn,pNom=pNom,pNumero=pNumero, pSuperType =pSuperType,pRarete=pRarete)
    return render_template("collection/recherche.jinja", lesPokemons = resultat, titre = "Recherche de pokemon")

@bp_collection.route('/ajout_carte', methods=["POST","GET"])
def ajouter():
    if request.method == "POST":
    
        id_pokemon = request.form.get("id_pokemon").strip()
        condition_pokemon = request.form.get('condition', default='').strip()
        cout_pokemon = request.form.get('cout', type=int, default=0)
        statut_pokemon = request.form.get('statut', default='').strip()

        message_condition = ''
        message_cout = ''
        message_statut = ''

        if not id_pokemon:
            abort(404, "paramêtre 'id_pokemon' invalide")

        invalide = False

        if not valide_condition(condition_pokemon):
            message_condition = 'is-invalid'
            invalide = True
        if not (cout_pokemon >= 0):
            message_cout = 'is-invalid'
            invalide = True
        if not valide_statut(statut_pokemon):
            message_statut = 'is-invalid'
            invalide = True

    if(invalide):
        with bd.creer_connexion() as conn:
            resultat=bd.selectionner(conn=conn,id=id_pokemon)
            return render_template("collection/ajout_carte.jinja", ajouterPokemon = resultat, titre = "Ajouter  une carte", 
                message_condition = message_condition, message_cout = message_cout, message_statut = message_statut)

    with bd.creer_connexion() as conn:
       bd.ajouter(conn=conn,id=id_pokemon,condition_pokemon=condition_pokemon,cout_pokemon=cout_pokemon,statut_pokemon=statut_pokemon)
    return redirect('/', code = 303)

@bp_collection.route('/modif_carte', methods=["POST"])
def modifier_carte():
    id_pokemon = request.form.get("id_pokemon").strip()
    if not id_pokemon :
        abort(404, "paramêtre 'id_pokemon' invalide") 
    condition_pokemon = request.form.get('condition', default='').strip()
    cout_pokemon = request.form.get('cout', type=int, default=0)
    statut_pokemon = request.form.get('statut', default='').strip()

    message_condition = ''
    message_cout = ''
    message_statut = ''


    invalide = False
    
    if not valide_condition(condition_pokemon):
        message_condition = 'is-invalid'
        invalide = True
    if not (cout_pokemon >= 0):
        message_cout = 'is-invalid'
        invalide = True
    if not valide_statut(statut_pokemon):
        message_statut = 'is-invalid'
        invalide = True

    if(invalide):
        with bd.creer_connexion() as conn:
            resultat = bd.selectionner(conn=conn,id=id_pokemon)
            return render_template("collection/modif_carte.jinja", ajouterPokemon = resultat, titre = "Ajouter  une carte", 
                message_condition = message_condition, message_cout = message_cout, message_statut = message_statut)

    with bd.creer_connexion() as conn:
        bd.modifier(conn,id,condition_pokemon,cout_pokemon,statut_pokemon)
        return redirect('/', code = 303)


@bp_collection.route('/detail', methods = ["GET","POST"])
def afficher_detail():
    id_pokemon = request.form.get("id_pokemon")
    if not id_pokemon :
        abort(404,"La carte n'existe pas")     
    else:
        with bd.creer_connexion() as conn:
           resultat = bd.afficher_detail(conn=conn,id=id_pokemon)
        if not resultat :
            abort(404,"La carte n'existe pas")
        return render_template("collection/detail.jinja", lePokemon = resultat, titre = "Détails")

def valide_condition(pCondition):
    """ Recoit la condition de la carte en paramêtre et retourne si elle est valide ou non """
    condition_values = ['presque neuve', 'légèrement usée', 'modérément usée', 'très usée', 'abîmée']
    for value in condition_values:
        if (pCondition == value):
            return True
    return False

def valide_statut(pStatut):
    """ Recoit le statut de la carte en paramêtre et retourne si il est valide ou non """
    statut_values = ['disponible', 'recherchée']
    for value in statut_values:
        if (pStatut == value):
            return True
    return False

def valide_supertype(pSupertype):
    """ Recoit le statut de la carte en paramêtre et retourne si il est valide ou non """
    supertype_values = ['','Pokémon', 'Trainer', 'Energy']
    for value in supertype_values:
        if (pSupertype == value):
            return True
    return False