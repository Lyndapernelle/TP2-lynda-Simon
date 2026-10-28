"""
Exercice de page de détails
"""

from flask import Flask, render_template, request, redirect, abort, url_for
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import bd
import re
import html
from config import Config
from collection import bp_collection

config = Config()
app = Flask(__name__)
logger = create_logger(app)

app.register_blueprint(bp_collection, url_prefix='/collection')



@app.route("/")
def index(): 
    pokemon = []
    with bd.creer_connexion() as conn:
        pokemon= bd.affiche_carte_accueil(conn=conn)
    return render_template("collection/index.jinja", lesPokemons = pokemon)        

@app.errorhandler(400)
def param_manquant(e):
    logger.exception(e)
    message = "Il manque un paramètres dans la requete "+ e.description
    return render_template("erreur.jinja",message = message),400

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

index()