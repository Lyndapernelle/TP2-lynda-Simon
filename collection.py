"""
Exercice de page de détails
"""

from flask import Flask, render_template, request, redirect, abort, Blueprint, url_for, session
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import uuid
from werkzeug.utils import secure_filename
import bd, os
import re
import html
from config import Config
bp_collection= Blueprint('collection', __name__)
chemin_import = os.path.join(bp_collection.root_path, *["static", "image", "imports"])

@bp_collection.route('/page_collection', methods=["GET", "POST"])
def page_de_collection():
    if not 'courriel' in session:
        abort(401,"")
    with bd.creer_connexion() as conn:
        pokemon = bd.affiche_carte_accueil(conn=conn,id_collectionneur = session['id'])
        return render_template("collection/page_collection.jinja", lesPokemons = pokemon)

@bp_collection.route('/recherche',methods=["GET"])
def recherche():
    if not 'courriel' in session:
        abort(401,"")
    pNom = request.args.get('nom_pokemon', default='').strip()
    pNumero = request.args.get('numero',type=int)
    pType = request.args.get('types', default='').strip()
    pRarete = request.args.get('rarete',default='').strip()
    pSuperType = request.args.get('supertype')
        
    if not valide_supertype(pType):
        abort(400," Paramètre 'superType' invalide")

    caracteres_interdits = re.compile('<(.*)>.*?|<(.*) />')

    if caracteres_interdits.match(pNom) :
        abort(400," Paramètre 'nom_pokemon' invalide")
    if caracteres_interdits.match(pRarete) :
        abort(400," Paramètre 'rarete' invalide")

    with bd.creer_connexion() as conn:
       resultat = bd.rechercher(conn=conn, pNom=pNom, pNumero=pNumero, pType=pType, pRarete=pRarete, pSuperType=pSuperType)
    return render_template("collection/recherche.jinja", lesPokemons = resultat, titre = "Recherche de pokemon")

@bp_collection.route('/ajout_carte/<string:pokemon_id>', methods=["POST","GET"])
def ajouter(pokemon_id):
    if request.method == "GET":
        with bd.creer_connexion() as conn:
            resultat = bd.selectionner(conn=conn,id=pokemon_id)
            return render_template('collection/ajout_carte.jinja', ajouterPokemon = resultat,cout = '',
            message_condition = '', message_cout = '', message_statut = '',message_image='') 
    elif request.method == "POST":
        condition_pokemon = request.form.get('condition', default='').strip()
        cout_pokemon = request.form.get('cout', type=int, default=0)
        statut_pokemon = request.form.get('statut', default='').strip()
        fichier = request.files.get('image')
        message_condition = ''
        message_cout = ''
        message_statut = ''
        message_image=''
        valide = True
        src =''
        if not pokemon_id:
            abort(404, "paramêtre 'id_pokemon' invalide")
            
        if not valide_condition(condition_pokemon):
            message_condition = 'Condition invalide'
            valide = False
        if not (cout_pokemon >= 0):
            message_cout = 'Cout invalide'
            valide = False
        if not valide_statut(statut_pokemon):
            message_statut = 'statut invalide'
            valide = False
        if fichier.filename:
            if (len(fichier.filename)<6 or len(fichier.filename)>50):
                message_image="Nom d'image Invalide"
                valide = False  
            else:
                nom_image = uuid.uuid4().hex[:5] + '_' + secure_filename(fichier.filename)
                chemin_complet = os.path.join(chemin_import, nom_image)
                fichier.save(chemin_complet)
                src = '/static/image/imports/'+ nom_image
        else:
            src='/static/image/image.jpeg'
            
        
    if (not valide):
            with bd.creer_connexion() as conn:
                resultat = bd.selectionner(conn=conn,id=pokemon_id)
                return render_template('collection/ajout_carte.jinja', ajouterPokemon = resultat, cout = cout_pokemon,
                message_condition = message_condition, message_cout = message_cout, message_statut = message_statut, message_image=message_image)    

    with bd.creer_connexion() as conn:
        bd.ajouter(conn=conn,id=pokemon_id,id_collectionneur=session['id'],condition_pokemon=condition_pokemon,cout_pokemon=cout_pokemon,statut_pokemon=statut_pokemon,src= src)
        return redirect(url_for('collection.page_de_collection'),
                                    code=303)
    

@bp_collection.route('/modif_carte/<string:id_pokemon>', methods=["POST","GET"])
def modifier_carte(id_pokemon):
    if request.method == "GET":
        with bd.creer_connexion() as conn:
            resultat = bd.selectionner(conn=conn,id=id_pokemon)
            return render_template("collection/modif_carte.jinja", ajouterPokemon = resultat, titre = "Modifier  une carte", 
                message_condition = '', message_cout = '', message_statut = '',cout = '')
    elif request.method == "POST": 
        if not id_pokemon :
            abort(404, "paramêtre 'id_pokemon' invalide") 

        condition_pokemon = request.form.get('condition', default='').strip()
        cout_pokemon = request.form.get('cout', type=int, default=0)
        statut_pokemon = request.form.get('statut', default='').strip()

        message_condition = ''
        message_cout = ''
        message_statut = ''

        valide = True
        
        if not valide_condition(condition_pokemon):
            message_condition = 'Condition invalide'
            valide = False
        if not (cout_pokemon >= 0):
            message_cout = 'Cout invalide'
            valide = False
        if not valide_statut(statut_pokemon):
            message_statut = 'statut invalide'
            valide = False

        if(not valide):
            with bd.creer_connexion() as conn:
                resultat = bd.selectionner(conn=conn,id=id_pokemon)
                return render_template("collection/modif_carte.jinja", ajouterPokemon = resultat, titre = "Modifier  une carte", 
                    message_condition = message_condition, message_cout = message_cout, message_statut = message_statut,cout = cout_pokemon)

        with bd.creer_connexion() as conn:
            bd.modifier(conn,id_pokemon,condition_pokemon,cout_pokemon,statut_pokemon)
            return redirect(url_for('collection.page_de_collection'), code = 303)


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

