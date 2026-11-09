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
                session['courriel'] = info['courriel']
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

@bp_comptes.route('/mot-de-passe', methods=["POST", "GET"])
def changer_mdp():
    if request.method == "GET":
        return render_template('compte/mot_de_passe.jinja', msg_mdp_invalide = '', msg_mdp_regex = '', msg_mdp_vide = '')
    elif request.method == "POST":

        mdp_actuel = request.form.get('mdp_actuel', default='').strip()
        mdp_nouv = request.form.get('nouveau_mdp', default='').strip()
        mdp_nouv_conf = request.form.get('nouveau_mdp_conf', default='').strip()
    
        regex_caractere_invalide = re.compile('<(.*)>.*?|<(.*) />')
        regex_mdp = re.compile('^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$')

        msg_mdp_invalide = ''
        msg_mdp_regex = ''
        msg_mdp_vide = ''
        msg_mdpconf_ivalide = ''
        valide_mdp = False
        nouv_mdp = False
        nouv_mdp_conf = False
   
        mdp_hasher = hasher_mdp(mdp_actuel)
        id_utilisateur = session['id']
        with bd.creer_connexion() as conn:
            mdp = bd.trouverCompte(conn = conn, mdp = mdp_hasher, id = id_utilisateur)
        if (mdp is None):
            valide_mdp = True
            msg_mdp_invalide = "Mot de passe invalide"
            return render_template('compte/mot_de_passe.jinja', valide_mdp=valide_mdp, msg_mdp_invalide=msg_mdp_invalide,
                                    nouv_mdp=nouv_mdp, msg_mdp_regex=msg_mdp_regex, msg_mdp_vide=msg_mdp_vide,
                                    nouv_mdp_conf=nouv_mdp_conf, msg_mdp_pas_pareil=msg_mdpconf_ivalide)

        elif (not mdp_actuel or not mdp_nouv or not regex_caractere_invalide.search(mdp_actuel) or not regex_mdp(mdp_actuel)):
            if (not mdp_actuel):
                valide_mdp = True
                msg_mdp_vide = 'Le champ ne peut être vide'
            if (not mdp_nouv):
                nouv_mdp = True
            if (not regex_caractere_invalide.search(mdp_actuel) or not regex_mdp(mdp_actuel)):
                nouv_mdp = True
                msg_mdp_regex = 'Le mot de passe est Invalide. Il doit contenir au moins 8 caractères, une lettre majuscule,' \
                ' une lettre minuscule, un chiffre'

            return render_template('compte/mot_de_passe.jinja', valide_mdp=valide_mdp, msg_mdp_invalide=msg_mdp_invalide,
                               nouv_mdp=nouv_mdp, msg_mdp_regex=msg_mdp_regex, msg_mdp_vide=msg_mdp_vide,
                               nouv_mdp_conf=nouv_mdp_conf, msg_mdp_pas_pareil=msg_mdpconf_ivalide)
        else:
            if (not mdp_nouv_conf or (not (mdp_nouv == mdp_nouv_conf))):
                if (not mdp_nouv_conf):
                    nouv_mdp_conf = True
                    msg_mdp_vide = 'Le champ ne peut être vide'
                elif not (mdp_nouv == mdp_nouv_conf):
                    nouv_mdp_conf = True
                    msg_mdpconf_ivalide = 'Veuillez écrire le même nouveau mot de passe'
                return render_template('compte/mot-de-passe.jinja', valide_mdp = valide_mdp, msg_mdp_invalide = msg_mdp_invalide,
                                    nouv_mdp = nouv_mdp, msg_mdp_regex = msg_mdp_regex, msg_mdp_vide = msg_mdp_vide,
                                    nouv_mdp_conf = nouv_mdp_conf, msg_mdp_pas_pareil = msg_mdpconf_ivalide)
            else:
                nouv_mdp_hasher = hasher_mdp(mdp_nouv)
                with bd.creer_connexion() as conn:
                    bd.changerMdp(conn = conn, nouv_mdp = nouv_mdp_hasher, id = id_utilisateur)
                    flash('Le mot de passe à été modifié avec succès','secces')
                    redirect('/', code=303)
                    
@bp_comptes.route('/remboursement')
def remboursement():
    if request.method == 'GET':
        return render_template('compte/remboursement.jinja')
    elif request.method == "POST":
        ### CODE



                    


   
        






def hasher_mdp(mdp_clair):
    return hashlib.sha512(mdp_clair.encode()).hexdigest()
