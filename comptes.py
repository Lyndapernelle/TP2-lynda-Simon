from flask import Flask, render_template, request, redirect, abort, Blueprint, url_for,session
from flask.logging import create_logger
from flask import flash
import mysql.connector
from mysql.connector import Error
import bd
import re
import html
import sys
import hashlib
from config import Config

bp_comptes = Blueprint('comptes', __name__)

@bp_comptes.route('/connexion', methods=["POST", "GET"])
def connexion():
    if request.method == "GET":
        return render_template("compte/connexion.jinja", titre="Retour vers la page de connexion")
    if request.method == "POST":

        bool_mdp = False
        bool_courriel = False
        courriel_utilisateur = request.form.get('courriel_compte', default='')
        mdp_clair = request.form.get('mdp_compte').strip()

        courriel_regex = re.compile('^[\w.]+@[\w.]+\.[a-zA-Z]{2,}$')
        mdp_regex = re.compile('^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$')

    if ((not courriel_regex.match(courriel_utilisateur)) or (not mdp_regex.match(mdp_clair))):
            if (not courriel_regex.match(courriel_utilisateur)):
                bool_courriel = True
            if (not mdp_regex.match(mdp_clair)):
                bool_mdp = True
            return render_template("compte/connexion.jinja", erreur_mdp = bool_mdp, erreur_courriel = bool_courriel)
    else:
        with bd.creer_connexion() as conn:
            utilisateur = bd.trouver_utilisateur(conn, courriel_utilisateur) 
            return render_template("menu/index.jinja", information_compte = utilisateur)

            
@bp_comptes.route('/creer', methods=["POST", "GET"])
def creer():
    if request.method == "GET":
        return render_template('compte/creer_compte.jinja',message_courriel= '', message_mdp= '', message_conf_mdp = '',
                                   courriel = '')
    elif request.method == "POST":
        courriel = request.form.get("courriel", default='').strip()
        mdp = request.form.get("mdp",default='').strip()
        conf_mdp=  request.form.get("conf_mdp", default='').strip()
        regex_caractere_invalide = re.compile('<(.*)>.*?|<(.*) />')
        regex_courriel = re.compile('^[\w.]+@[\w.]+\.[a-zA-Z]{2,}$')
        regex_mdp = re.compile('^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$')
        valide = True
        erreur_courriel = ''
        erreur_mdp=''
        erreur_conf_mdp=''

        if not courriel or not regex_courriel.match(courriel) or regex_caractere_invalide.match(courriel): 
            valide = False
            erreur_courriel = 'Courriel Invalide'
        if not mdp or not regex_mdp.match(mdp) or regex_caractere_invalide.match(mdp):
            valide = False
            erreur_mdp = 'Le mot de passe est Invalide. Il doit contenir au moins 8 caractères, une lettre majuscule,' \
            ' une lettre majuscule, un chiffre'
        if not valide:
            return render_template('compte/creer_compte.jinja',message_courriel= erreur_courriel, message_mdp= erreur_mdp, message_conf_mdp = '',
                                   courriel = courriel)
        else:
            if not (mdp == conf_mdp):
                erreur_conf_mdp = 'Les mots de passe doivent être identiques'
                return render_template('compte/creer_compte.jinja',message_courriel= erreur_courriel, message_mdp= erreur_mdp, message_conf_mdp = erreur_conf_mdp,
                                                   courriel = courriel)
            else:
                mdp_hash = hasher_mdp(mdp)
                try:
                    with bd.creer_connexion() as conn:
                        bd.creer_compte(conn=conn, courriel = courriel, mdp_hash = mdp_hash)
                        flash('Le compte a été crée','succes')
                        return redirect('/',code=303)
                except Exception :
                                flash('La création de compte a échoué','erreur')
                                abort(500,"Le serveur a rencontré une erreur")
            







def hasher_mdp(mdp_clair):
    return hashlib.sha512(mdp_clair.encode()).hexdigest()
