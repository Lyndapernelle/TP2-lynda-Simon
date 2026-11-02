from flask import Flask, render_template, request, redirect, abort, Blueprint, url_for
from flask.logging import create_logger
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

        erreur_courriel = False
        erreur_mdp = False
        courriel_utilisateur = request.form.get('courriel_compte', default='')
        mdp_clair = request.form.get('mdp_compte').strip()

        courriel_regex = re.compile('^[\w.]+@[\w.]+\.[a-zA-Z]{2,}$')
        mdp_caractere_interdit = re.compile('^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$')

        if (courriel_utilisateur.islower()):
            ### Si le courriel est d'abors faux, ensuite on vérifie le reste
            if (not courriel_regex.match(courriel_utilisateur)):
                erreur_courriel = True 
                if not mdp_caractere_interdit.match(mdp_clair):
                    erreur_mdp = True
                    return render_template('compte/connexion.jinja', erreur_courriel = erreur_courriel, erreur_mdp = erreur_mdp)
                else:
                    return render_template("compte/connexion.jinja", erreur_courriel = erreur_courriel)
            ### Si le mot de passe est d'abors faux, ensuite on vérifie le reste
            elif not mdp_caractere_interdit.match(mdp_clair):
                erreur_mdp = True
                if (not courriel_regex.match(courriel_utilisateur)):
                    erreur_courriel = True
                    return render_template("compte/connexion.jinja", erreur_mdp = erreur_mdp, erreur_courriel = erreur_courriel)
                else:
                    return render_template("compte/connexion.jinja", erreur_mdp = erreur_mdp)
            else:
                with bd.creer_connexion() as conn:
                    utilisateur = bd.trouver_utilisateur(conn, courriel_utilisateur) 
                    return render_template("menu/index.jinja", information_compte = utilisateur)
                
        elif(not courriel_utilisateur.islower()):
            erreur_courriel = True
            if not mdp_caractere_interdit.match(mdp_clair):
                erreur_mdp = True
                return render_template('compte/connexion.jinja', erreur_courriel = erreur_courriel, erreur_mdp = erreur_mdp)
            else:
                return render_template("compte/connexion.jinja", erreur_courriel = erreur_courriel)
            
   







def hasher_mdp(mdp_clair):
     hashlib.sha512(mdp_clair.encode()).hexdigest()
