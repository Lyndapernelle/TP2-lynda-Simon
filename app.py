from flask import Flask, render_template, session, flash, redirect
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import bd
import uuid
from werkzeug.utils import secure_filename

import re
import os
import html
from config import Config
from collection import bp_collection
from comptes import bp_comptes

config = Config()
app = Flask(__name__)
logger = create_logger(app)

app.secret_key = "f78bde7e6d92cfdf4d58392353e16032bb79417924d30ad7b6c733f00131ca71"



app.register_blueprint(bp_collection, url_prefix='/collection')
app.register_blueprint(bp_comptes, url_prefix='/compte')

@app.route('/')
def index():
    if 'courriel' in session:
        session.permanent = True
    else: 
        flash('Veuillez vous connecter','erreur')
    with bd.creer_connexion() as conn:
        pokemon = bd.accueil_invite(conn=conn)
        return render_template("menu/index.jinja", lesPokemons = pokemon)

@app.route('/Deconnecter')
def detruire_session():
    session.clear()
    flash('Déconnexion du compte effectué avec succes','succes')
    return redirect('/', code=303)
    
@app.errorhandler(400)
def param_manquant(e):
    logger.exception(e)
    message = "Il manque un paramètres dans la requete "+ e.description
    return render_template("erreur.jinja",message = message),400

@app.errorhandler(401)
def element_inexistant(e):
    logger.exception(e)
    message = "Vous devez vous connecter pour avoir accès à cette page "+e.description
    return render_template("erreur_acces.jinja",message = message),401

@app.errorhandler(403)
def element_inexistant(e):
    logger.exception(e)
    message = "Accès Interdit"+e.description
    return render_template("erreur_acces.jinja",message = message),403

@app.errorhandler(404)
def element_inexistant(e):
    logger.exception(e)
    message = "Élément inexistant "+e.description
    return render_template("erreur.jinja",message = message),404

@app.errorhandler(500)
def erreur_bd(e):
    logger.exception(e)

    message = e.description

    if e.original_exception and isinstance(e.original_exception, mysql.connector.errors.Error):
        message = "Erreur en lien avec la base de donnée."

    return render_template("erreur.jinja", message=message),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=config.APP_ENV.lower() == "local")