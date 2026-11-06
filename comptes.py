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

            
   







def hasher_mdp(mdp_clair):
     hashlib.sha512(mdp_clair.encode()).hexdigest()
