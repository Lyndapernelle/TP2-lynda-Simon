"""
Connexion à la BD
"""

import types
import contextlib
import mysql.connector
from config import Config
from flask import abort
from flask import flash
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

def accueil_invite(conn):
    with conn.get_curseur() as curseur:
        try:
            curseur.execute(
                "select ci.id, ci.condition, ci.cost, ci.status, ci.photo, " +
                "pc.name, pc.set_num, pc.types, pc.rarity " +
                "FROM collection_items ci " +
                "JOIN pokemon_card pc ON pc.id = ci.card_id " +
                "WHERE ci.status like 'disponible' " +
                "ORDER BY ci.added_date DESC " +
                "limit 10"
            )
        except Exception:
            abort(500,"Le serveur a rencontré une erreur.")
        pokemon = curseur.fetchall()
        return pokemon

def affiche_carte_accueil(conn,id_collectionneur):
    with conn.get_curseur() as curseur:
                try:
                    curseur.execute(
                "SELECT ci.id, ci.`condition`, ci.cost, ci.status, ci.photo, pc.name, pc.set_num, pc.types, pc.rarity "
                "FROM collection_items ci "
                "JOIN pokemon_card pc ON pc.id = ci.card_id "
                "WHERE ci.id_collectionneur = %(id_collectionneur)s "
                "ORDER BY ci.added_date DESC",
                {
                    'id_collectionneur': id_collectionneur
                }
                )
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                pokemon = curseur.fetchall()
                return pokemon

def rechercher(conn, pNom, pNumero, pType, pRarete, pSuperType):
      with conn.get_curseur() as curseur:
                try:
                    curseur.execute("select id, name, set_num, types, supertype ,rarity from pokemon_card "+
                    "where name like %(nom_pokemon)s and "+
                    "(set_num = %(numero)s or %(numero)s is null) and "+
                    "(types = %(type_pokemon)s or %(type_pokemon)s = '') and "+
                    "rarity like %(rarete_pokemon)s and "+
                    "supertype = %(supertype_pokemon)s order by name "+
                    "LIMIT 50",
                    {
                        'nom_pokemon':'%'+pNom+'%',
                        'numero' : pNumero,
                        'type_pokemon' : pType,
                        'rarete_pokemon' : '%'+pRarete+'%',
                        'supertype_pokemon' : pSuperType
                    }
                    )        
             
                except Exception:
                    abort(500,"Le serveur a rencontré une erreur.")
                resultat = curseur.fetchall()
                return resultat     

def afficher_detail(conn,id):
      with conn.get_curseur() as curseur:
                     try:
                         curseur.execute("select pc.*, ci.added_date, ci.condition, ci.cost, ci.status,ci.photo" +
                         " from collection_items ci"+
                         " join pokemon_card pc on pc.id = ci.card_id"+
                         " where ci.id = %(id)s",
                         {
                             'id': id
                         })
                     except Exception:
                         abort(500,"Le serveur a rencontré une erreur.")
                     resultat = curseur.fetchone()
                     return resultat

def modifier(conn,id_pokemon,condition_pokemon,cout_pokemon,statut_pokemon):
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
                'pokemon_status' : statut_pokemon

            })
        except Exception:
            abort(500,"Le serveur a rencontré une erreur.")

def selectionner(conn, id):
    with conn.get_curseur() as curseur:
        curseur.execute("select * from pokemon_card where id = %(id_pokemon)s",
        {
            'id_pokemon' : id
        }
        )
        resultat = curseur.fetchone()
        return resultat

def ajouter(conn,id,id_collectionneur,condition_pokemon,cout_pokemon,statut_pokemon,src):
       with conn.get_curseur() as curseur:
            try:
                curseur.execute("INSERT INTO collection_items (`id_collectionneur`,`card_id`, `condition`, `cost`, `status`,`photo`) "
                "VALUES(%(id_collectionneur)s,%(card_id)s, %(condition)s, %(cout)s, %(status)s,%(src)s)",
                {
                    'id_collectionneur': id_collectionneur,
                    'card_id' : id,
                    'condition' : condition_pokemon,
                    'cout' : cout_pokemon,
                    'status' : statut_pokemon,
                    'src' : src
                }
            )
            except Exception as e:
                print("ERREUR SQL :", repr(e), flush=True)
                abort(500, "Le serveur a rencontré une erreur")

def trouver_utilisateur(conn,courriel,mdp_hash):
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT * from collectionneurs " 
        "WHERE courriel = %(courriel)s "
        "AND mot_de_passe = %(mdp_hash)s",
        {
            'courriel' : courriel, 
            'mdp_hash' : mdp_hash
        }
        )
        return curseur.fetchone()

def trouver_courriel(conn,courriel_utilisateur):
    with conn.get_curseur() as curseur:
        try:
            curseur.execute("SELECT * from collectionneurs " 
            "where courriel = %(courriel)s",
            {
                'courriel' : courriel_utilisateur  
            }
            )
            return curseur.fetchone()
        except Exception :
            abort(500,"Le serveur a rencontré une erreur")
def creer_compte(conn,courriel,mdp_hash):
    with conn.get_curseur() as curseur:
        curseur.execute("INSERT INTO collectionneurs (`courriel`,`mot_de_passe`,`credit`)"
        "VALUES(%(courriel)s, %(mdp_hash)s, 100)",
        {
            'courriel': courriel,
            'mdp_hash': mdp_hash
        })

def lister_utilisateur(conn):
    with conn.get_curseur() as curseur:
        try:
            curseur.execute("SELECT * from collectionneurs ")
            pokemon = curseur.fetchall()
            return pokemon
        except Exception :
            abort(500,"Le serveur a rencontré une erreur")

def cartes_utilisateur(conn,courriel):
    with conn.get_curseur() as curseur:
        try:
            curseur.execute( "SELECT ci.id, ci.`condition`, ci.cost, ci.status, ci.added_date, ci.photo, "
            "pc.name, pc.set_num, pc.types, pc.rarity "
            "FROM collection_items ci "
            "JOIN collectionneurs c ON c.id = ci.id_collectionneur "
            "JOIN pokemon_card pc ON pc.id = ci.card_id "
            "WHERE c.courriel = %(courriel)s ORDER BY ci.added_date DESC",
            {
                'courriel': courriel
            }
            )
            informations = curseur.fetchall()
            return informations
        except Exception :
            abort(500,"Le serveur a rencontré une erreur")

def obtenir_credit(conn, courriel):
    with conn.cursor() as curseur:
        curseur.execute(
            "SELECT credit FROM collectionneurs WHERE courriel = %(courriel)s",
            {
                'courriel': courriel
            }
        )
        resultat = curseur.fetchone()
        return resultat[0]