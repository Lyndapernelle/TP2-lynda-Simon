"""
Exercice de page de détails
"""

from flask import Flask, render_template, request, redirect, abort
from flask.logging import create_logger
import mysql.connector
from mysql.connector import Error
import bd
import re
import html
from config import Config


config = Config()
app = Flask(__name__)
logger = create_logger(app)

@app.route("/")
def index(): 
    pokemon = []
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            try:
                curseur.execute(
                    "select ci.id, ci.condition, ci.cost, ci.status, " +
                    "pc.name, pc.set_num, pc.types, pc.rarity " +
                    "FROM collection_items ci " +
                    "JOIN pokemon_card pc ON pc.id = ci.card_id " +
                    "WHERE ci.status like 'disponible' " +
                    "ORDER BY ci.added_date DESC " +
                    "limit 5"
                )
            except Exception:
                abort(500,"Le serveur a rencontré une erreur.")
            pokemon = curseur.fetchall()
    return render_template("index.jinja", lesPokemons = pokemon)        

def afficher_carte():
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            try:
                curseur.execute("select * from pokemon_card LIMIT 50")
            except Exception:
                abort(500,"Le serveur a rencontré une erreur.")
            resultat = curseur.fetchall()
    return render_template("recherche.jinja",lesPokemons = resultat, titre = "Recherche de pokemon")

@app.route("/recherche", methods = ["GET","POST"])
def recherche():
    if request.method == 'POST':
        nom = request.form.get('nom_pokemon', default='')
        if not nom:
            abort(400," Paramètre 'Nom' manquant")

        numero = request.form.get('numero',type=int)
        if not numero:
            abort(400," Paramètre 'Numéro' manquant")

        superType = request.form.get('supertype')
        if not superType:
            abort(400," Paramètre 'Super Type' manquant")

        rarete = request.form.get('rarete',default='')
        if not rarete:
           abort(400," Paramètre 'Rareté' manquant")
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                try:
                    curseur.execute("select id, name, set_num, supertype, rarity from pokemon_card "+
                    "where name like %(nom_pokemon)s and "+
                    "(set_num = %(numero)s or %(numero)s is null) and "+
                    "supertype = %(supertype)s and "+
                    "rarity like %(rarete_pokemon)s order by name "+
                    "LIMIT 50",
                    {
                        'nom_pokemon':'%'+nom+'%',
                        'numero' : numero,
                        'supertype' : superType,
                        'rarete_pokemon' : '%'+rarete+'%'
                    }
                    )
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                resultat = curseur.fetchall()
        return render_template("recherche.jinja", lesPokemons = resultat, titre = "Recherche de pokemon")
    else:
         return afficher_carte()

@app.route('/recuperation_carte_ajout', methods= ["POST", "GET"])
def recuperation_id_ajout():
    if request.method == "POST":
        id_pokemon_string = request.form.get('id_pokemon')
        if not id_pokemon_string:
            abort(400," Paramètre 'Id' manquant")
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                try:
                    curseur.execute("select * from pokemon_card where id = %(id_pokemon)s",
                    {
                        'id_pokemon' : id_pokemon_string
                    }
                    )
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                resultat = curseur.fetchone()
                return render_template("ajout_carte.jinja", ajouterPokemon = resultat, titre = "Ajouter une carte")
    return render_template("ajout_carte.jinja", ajouterPokemon = "", titre = "Ajouter une carte")

@app.route('/ajout_carte', methods=["POST"])
def ajouter_carte():
    id_pokemon = request.form.get('id_pokemon')
    if not id_pokemon :
        abort(404,"La carte n'existe pas")  

    condition_pokemon = request.form.get('condition')
    if not condition_pokemon:
        abort(400," Paramètre 'Condition' manquant")

    cout_pokemon = request.form.get('cout')
    if not cout_pokemon:
        abort(400," Paramètre 'Coût' manquant")

    statut_pokemon = request.form.get('statut')
    if not statut_pokemon:
        abort(400," Paramètre 'Statut' manquant")
    with bd.creer_connexion() as conn:
        with conn.get_curseur() as curseur:
            try:
                curseur.execute("INSERT INTO collection_items (`card_id`, `condition`, `cost`, `status`) "
                "VALUES(%(card_id)s, %(condition)s, %(cout)s, %(status)s)",
                {
                    'card_id' : id_pokemon,
                    'condition' : condition_pokemon,
                    'cout' : cout_pokemon,
                    'status' : statut_pokemon
                }
            )
            except Exception:
                abort(500,"Le serveur a rencontré une erreur.")
    return redirect('/', code = 303)

@app.route('/recuperation_carte_modif', methods= ["POST", "GET"])
def recuperation_id_modif():
    if request.method == "POST":
        id_pokemon_string = request.form.get('id_pokemon')
        if not id_pokemon_string :
            abort(404,"La carte n'existe pas")  
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                try:
                    curseur.execute("select * from pokemon_card where id = %(id_pokemon)s",
                    {
                        'id_pokemon' : id_pokemon_string
                    }
                    )
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                resultat = curseur.fetchone()
                return render_template("modif_carte.jinja", ajouterPokemon = resultat, titre = "Modification d'une carte")
    return render_template("modif_carte.jinja", ajouterPokemon = "", titre = "Modification d'une carte")

@app.route('/modif_carte', methods=["POST","GET"])
def modifier_carte():
    if request.method=="POST":
        id_pokemon = request.form.get("id_pokemon")
        if not id_pokemon :
            abort(404,"La carte n'existe pas")  
        condition_pokemon = request.form.get('condition')
        if not condition_pokemon:
            abort(400," Paramètre 'Condition' manquant")
            
        cout_pokemon = request.form.get('cout')
        if not cout_pokemon:
            abort(400," Paramètre 'Coût' manquant")

        status_pokemon = request.form.get('statut')
        if not status_pokemon:
            abort(400," Paramètre 'Statut' manquant")
        with bd.creer_connexion() as conn:
            with conn.get_curseur() as curseur:
                try:
                    curseur.execute("UPDATE collection_items "
                    "SET status = %(pokemon_status)s, "
                    "cost = %(pokemon_cout)s, "
                    "`condition` = %(pokemon_condition)s " 
                    "WHERE card_id = %(pokemon_id)s ",
                    {
                        'pokemon_id' : id_pokemon,
                        'pokemon_condition' : condition_pokemon,
                        'pokemon_cout' : cout_pokemon,
                        'pokemon_status' : status_pokemon

                    })
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                return redirect('/', code = 303)


@app.route('/detail', methods = ["POST"])
def afficher_detail():
    if request.method=="POST":
        id_pokemon = request.form.get('id_pokemon')
        if not id_pokemon :
            abort(404,"La carte n'existe pas")     
        else:
            with bd.creer_connexion() as conn:
                with conn.get_curseur() as curseur:
                    try:
                        curseur.execute("select pc.*, ci.added_date, ci.condition, ci.cost, ci.status" +
                        " from collection_items ci"+
                        " join pokemon_card pc on pc.id = ci.card_id"+
                        " where ci.id = %(id)s",
                        {
                            'id': id_pokemon
                        })
                    except Exception:
                        abort(500,"Le serveur a rencontré une erreur.")
                    resultat = curseur.fetchone()
            if not resultat :
                abort(404,"La carte n'existe pas")
            return render_template("detail.jinja", lePokemon = resultat, titre = "Détails")

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