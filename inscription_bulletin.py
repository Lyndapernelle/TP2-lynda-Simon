from flask import Flask, render_template, request, redirect, abort, Blueprint
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import bd
import re
import html
from config import Config

bp_bulletin= Blueprint('inscription_bulletin', __name__)

@bp_bulletin.route('/',methods=["POST","GET"])
def inscrire():
    if request.method == 'POST':
        courriel = request.form.get("courriel",default="")
        a_accepte = request.form.get("chk-conf")
        frequence  = request.form.get("frequence")
        frequence_valeur = ['quotidien', 'hebdomadaire','mensuel']
        regex_courriel = re.compile('[A-Za-z0-9]+@[\w]+\.[\w]+')

        message_erreur_select=""
        message_erreur_courriel=""
        message_erreur_check=""
        if not regex_courriel.fullmatch(courriel):
            message_erreur_courriel = "courriel Invalide"
            message_erreur_select=""
            message_erreur_check=""
            return render_template("inscription_bulletin/inscription_bulletin.jinja", message_erreur_courriel=message_erreur_courriel,
                                   message_erreur_check=message_erreur_check,message_erreur_select=message_erreur_select)
        elif a_accepte == False:
            message_erreur_check = "Vous devez accepter pour continuer"
            message_erreur_select=""
            message_erreur_courriel=""
            return render_template("inscription_bulletin/inscription_bulletin.jinja", message_erreur_courriel=message_erreur_courriel,
                                               message_erreur_check=message_erreur_check,message_erreur_select=message_erreur_select)
        elif frequence not in frequence_valeur:
            message_erreur_select = "Vous devez séelctionner une fréquence valide"
            message_erreur_courriel=""
            message_erreur_check=""
            return render_template("inscription_bulletin/inscription_bulletin.jinja", message_erreur_courriel=message_erreur_courriel,
                                                           message_erreur_check=message_erreur_check,message_erreur_select=message_erreur_select)
        else:
            with bd.creer_connexion() as conn:
                lastId = bd.inscrire(conn=conn,courriel=courriel,frequence=frequence)
                redirect('/confirmation/?id='+lastId, code=303)
    else:
        return render_template("inscription_bulletin/inscription_bulletin.jinja", message_erreur_courriel="",
                                                       message_erreur_check="",message_erreur_select="")

@bp_bulletin.route('/confirmation/<id>')
def confirmer(id):
    return render_template('inscription_bulletin/confirmation.jinja', idAjoute=id )

@bp_bulletin.route('/modifier',methods=["GET"])
def modifier():
    courriel = request.args.get("courriel")
    message_erreur_courriel=""
    with bd.creer_connexion() as conn:
        resultat = bd.recherche_courriel(conn=conn,courriel=courriel)
    if resultat is None:
        redirect('/inscription/modifier/?id='+resultat, code=303)
    else:
        message_erreur_courriel = "Le courriel n'existe pas"
        return render_template("inscription_bulletin/inscription_bulletin.jinja", message_erreur_courriel=message_erreur_courriel)



@bp_bulletin.route('/modifier/<id>')
def modifier_id(id):
    return render_template("modifier.jinja")
