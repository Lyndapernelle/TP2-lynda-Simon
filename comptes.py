from flask import Flask, render_template, request, redirect, abort, Blueprint, url_for, session
from flask.logging import create_logger
from flask import current_app
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
        return render_template('compte/connexion.jinja', titre="Retour vers la page de connexion")
    if request.method == "POST":

        valide_mdp = False
        valide_courriel = False
        courriel_utilisateur = request.form.get('courriel', default='').strip()
        mdp_clair = request.form.get('mdp').strip()
        courriel_regex = re.compile('^[\w.]+@[\w.]+\.[a-zA-Z]{2,}$')
        mdp_regex = re.compile('^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$')

        message_courriel_vide = ''
        message_mdp_vide = ''
        msg_compte_inexistant = ''
        message_mdp_regex = ''
        message_courriel_regex = ''

        if (not courriel_utilisateur or not mdp_clair or not courriel_regex.match(courriel_utilisateur) or not mdp_regex.match(mdp_clair)):
            if (not courriel_utilisateur):
                valide_courriel = True
                message_courriel_vide = "Veuillez entrer un courriel"
            elif (not courriel_regex.match(courriel_utilisateur)):
                    valide_courriel = True
                    message_courriel_regex = 'Le courriel doit ressembler à ceci : nom@domaine.com'
            if (not mdp_clair):
                valide_mdp = True
                message_mdp_vide = "Veuillez entrer un mot de passe"  
            elif (not mdp_regex.match(mdp_clair)):
                valide_mdp = True
                message_mdp_regex = "Ce mot de passe de correspond pas à nos exigences"
            return render_template('compte/connexion.jinja', erreur_mdp = valide_mdp, erreur_courriel = valide_courriel, 
                                    courriel = courriel_utilisateur, msg_inexistant = msg_compte_inexistant,
                                    msg_courriel_vide = message_courriel_vide, msg_mdp_vide = message_mdp_vide,
                                    msg_courriel_regex = message_courriel_regex, msg_mdp_regex = message_mdp_regex
                                )
        else:  
            mdp_hash = hasher_mdp(mdp_clair)
            try:
                with bd.creer_connexion() as conn:
                    info = bd.trouver_utilisateur(conn = conn, courriel = courriel_utilisateur, mdp_hash = mdp_hash)
            except Exception:
                flash('Le recherche de compte à échoué','erreur')
                abort(500,"Le serveur a rencontré une erreur")
            if (info is None):
                valide_mdp = True
                valide_courriel = True
                msg_compte_inexistant = 'Le courriel ou le mot de passe est incorrect, veuillez réessayer'
                return render_template('compte/connexion.jinja', erreur_mdp = valide_mdp, erreur_courriel = valide_courriel, 
                                        courriel = courriel_utilisateur, msg_inexistant = msg_compte_inexistant,
                                        msg_courriel_vide = message_courriel_vide, msg_mdp_vide = message_mdp_vide,
                                        msg_courriel_regex = message_courriel_regex, msg_mdp_regex = message_mdp_regex
                                    )
            else:
                session['courriel'] = courriel_utilisateur
                session['id'] = info['id']
                flash('Connexion au compte effectué avec succès','succes')
                return redirect("/", code=303)              
           

       
@bp_comptes.route('/creer', methods=["POST", "GET"])
def creer():
    if not 'courriel' in session:
        abort(401,"")
    elif session['courriel'] != 'admin@garneau.ca':
        abort(403,"")
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
        valide_mdp = True
        valide_conf_mdp = True
        valide_courriel = True
        erreur_courriel = ''
        erreur_mdp=''
        erreur_conf_mdp=''

        if not courriel or not regex_courriel.match(courriel) or regex_caractere_invalide.search(courriel): 
            valide_courriel = False
            erreur_courriel = 'Courriel Invalide'
        if not mdp or not regex_mdp.match(mdp) or regex_caractere_invalide.search(mdp):
            valide_mdp = False
            erreur_mdp = 'Le mot de passe est Invalide. Il doit contenir au moins 8 caractères, une lettre majuscule,' \
            ' une lettre minuscule, un chiffre'
        if not valide_courriel or not valide_mdp :
            return render_template('compte/creer_compte.jinja',message_courriel= erreur_courriel, message_mdp= erreur_mdp, message_conf_mdp = '',
                                   courriel = courriel)
        else:
            if not (mdp == conf_mdp):
                valide_conf_mdp = False
                erreur_conf_mdp = 'Les mots de passe doivent être identiques'
                return render_template('compte/creer_compte.jinja',message_courriel= erreur_courriel, message_mdp= erreur_mdp, message_conf_mdp = erreur_conf_mdp,
                                                   courriel = courriel)
            else:
                mdp_hash = hasher_mdp(mdp)
                with bd.creer_connexion() as conn:
                    info = bd.trouver_courriel(conn = conn, courriel_utilisateur=courriel)
                    if (info is None):
                        try:
                            bd.creer_compte(conn=conn, courriel = courriel, mdp_hash = mdp_hash)
                            flash('Le compte a été crée','succes')
                            return redirect('/',code=303)
                        except Exception :
                            flash('La création de compte a échoué','erreur')
                            abort(500,"Le serveur a rencontré une erreur")
                    else:
                        erreur_courriel='Ce courriel est déjà utilisé'
                        return render_template('compte/creer_compte.jinja',message_courriel= erreur_courriel, message_mdp= erreur_mdp, message_conf_mdp = '',
                                                           courriel = courriel)
@bp_comptes.route('/liste_utilisateur')
def lister_utilisateur():
    if not 'courriel' in session:
        abort(401,"")
    elif session['courriel'] != 'admin@garneau.ca':
        abort(403,"")
    with bd.creer_connexion() as conn:
        resultat = bd.lister_utilisateur(conn=conn)
        return render_template('compte/liste_utilisateur.jinja',resultat = resultat, titre = 'Utilisateurs')

@bp_comptes.route('/liste_utilisateur/<courriel>',methods=["GET"])
def detail_utilisateur(courriel):
    if not courriel:
        abort(400,"  Courriel manquant") 
    else:
        with bd.creer_connexion() as conn:
            credit= bd.obtenir_credit(conn=conn,courriel=courriel)
            cartes = bd.cartes_utilisateur(conn=conn,courriel=courriel)
            return render_template('compte/detail_utilisateur.jinja',cartes = cartes, courriel = courriel, credit = credit, titre= 'Information du compte')





def hasher_mdp(mdp_clair):
    return hashlib.sha512(mdp_clair.encode()).hexdigest()
