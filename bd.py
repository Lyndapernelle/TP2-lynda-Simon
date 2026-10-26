"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector
from config import Config
from flask import abort

config = Config


@contextlib.contextmanager
def creer_connexion():
    """Pour créer une connexion à la BD"""
    conn = mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_DATABASE,
        raise_on_warnings=True,
    )

    # Pour ajouter la méthode getCurseur() à l'objet connexion
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextlib.contextmanager
def get_curseur(self):
    """Permet d'avoir les enregistrements sous forme de dictionnaires"""
    curseur = self.cursor(dictionary=True)
    try:
        yield curseur
    finally:
        curseur.close()

def affiche_carte_accueil(conn):
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
                return pokemon

def rechercher(conn, pNom,pNumero,pSuperType,pRarete):
      with conn.get_curseur() as curseur:
                try:
                    curseur.execute("select id, name, set_num, supertype, rarity from pokemon_card "+
                    "where name like %(nom_pokemon)s and "+
                    "(set_num = %(numero)s or %(numero)s is null) and "+
                    "(supertype = %(supertype)s or %(supertype)s = '') and "+
                    "rarity like %(rarete_pokemon)s order by name "+
                    "LIMIT 50",
                    {
                        'nom_pokemon':'%'+pNom+'%',
                        'numero' : pNumero,
                        'supertype' : pSuperType,
                        'rarete_pokemon' : '%'+pRarete+'%'
                    }
                    )
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                resultat = curseur.fetchall()
                return resultat