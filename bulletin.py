from flask import Flask, Blueprint, render_template, request, redirect, re
import bd

bp_inscription_bulletin = Blueprint('bulletin', __name__)


@bp_inscription_bulletin.route('/inscription_bulletin')
def inscription():
    return render_template("inscription_bulletin/formulaire_bulletin.jinja", titre="Inscription Info Lettre")


@bp_inscription_bulletin.route('/formulaire_bulletin', methods=["POST"])
def confirmation():
    courriel = request.form.get('mail_utilisateur').strip()
    frequence = request.form.get('frequence').strip()

    regex_courriel = re.compile ("[A-Za-Z0-9]+@[\w]+\.[\w]+")
    if regex_courriel.match(courriel) is not None:
        courriel.__class__.__add__('is-invalide')
        print(f'Le courriel est validé !')
    else: 
        print(f'Veuillez écrire un courriel valide !')
    return redirect('/confirmation_bulletin')

@bp_inscription_bulletin.route('/confirmation_bulletin', methods=["GET"])
def  confirmationInscription():  
   
