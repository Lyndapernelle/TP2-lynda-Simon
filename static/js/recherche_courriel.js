"use strict";

let courriel = null;
let controleur = null;
let controlleur2 = null;
let liste_utilisateur = null;
let contenuInitial = null;
let btn_ajout = document.getElementById('form-ajout');
function afficher_erreur(messsage){
    const div = document.createElement('div')
    div.classList.add('text-center')

    const image = document.createElement("img");
    image.src = '../static/image/iconeVide.png'
    image.alt = 'Aucun résultat'
    image.classList.add('w-75')
    
    const p = document.createElement("p");
    p.textContent= messsage
    p.classList.add('fs-2', 'fw-bold', 'mt-3')

    div.append(image);
    div.append(p);
    return div;

}


function creerBouton(texte, url) {
    const lien = document.createElement("a");
    lien.href = url;
    lien.className = "btn btn-primary btn-sm mt-1 mb-1 rounded-pill";
    lien.textContent = texte;
    return lien;
}

function creerUtilisateur(utilisateur) {
    const carte = document.createElement("div");
    carte.className = "card";
    carte.style.width = "15rem";

    const img = document.createElement("img");
    img.src = "../static/image/image_utilisateur.png";
    img.className = "card-img-top";
    img.alt = "Image utilisteur";
    carte.append(img);

    const corps = document.createElement("div");
    corps.className = "card-body";
    const titre = document.createElement("h5");
    titre.className = "card-title";
    titre.textContent = utilisateur.courriel;
    corps.append(titre);
    carte.append(corps);

    const bouton= creerBouton("Afficher les détails", `/liste_utilisateur/${utilisateur.courriel}`);
    bouton.className = "btn btn-primary m-3";
    carte.append(bouton);

    return carte;
}

async function rechercher_courriel() {
    const achercher = courriel.value.trim();
    if (controleur != null) {
        controleur.abort();
    }
    
    if(achercher.length <3){
        liste_utilisateur.innerHTML = contenuInitial
        return;
    }
    controleur = new AbortController()

    const parametres = {
    "mot_cle": achercher,
    }
    try {
        const resultat = await envoyerRequeteAjax(
        "/api/recherche-compte",
        "GET",
        parametres, 
        controleur     
        );
        
        liste_utilisateur.textContent="";
        if (resultat.length===0) {
            const messsage='Aucun résultat  🥀'
            const div= afficher_erreur(messsage)
            liste_utilisateur.append(div);
            return;
        }

        resultat.forEach(utilisateur => {
            const carte_utilisateur = creerUtilisateur(utilisateur);
            liste_utilisateur.append(carte_utilisateur);
        });
        controleur = null
    } catch (err) {
        if (err.name === "AbortError") {
            console.log("Une requête Ajax a été annulée")
        } else {
            console.error("Erreur lors d'une requête Ajax");
            console.error(err);
            liste_utilisateur.textContent = "Erreur lors de la requête. Veuillez réessayer."
        }
    }
}

async function ajouter(event) {
    if (controlleur2 != null) {
        controlleur2.abort();
    }
    event.preventDefault();
    let n = Math.floor(Math.random() * 100)
    let courriel = `admin${n}@cegepgarneau.ca`
    let mdp = 'Qwerty123'

    controlleur2 = new AbortController()
    const parametres = {
    "courriel": courriel,
    "mdp": mdp
    }
    try {
        const resultat = await envoyerRequeteAjax(
        "/api/creer-compte-rapide",
        "POST",
        parametres, 
        controleur     
        );
        if (resultat === null) {
            const messsage='Echec de la création  🥀'
            const div= afficher_erreur(messsage)
            liste_utilisateur.append(div);
            return;
        }
        const carte_utilisateur = creerUtilisateur(resultat);
        liste_utilisateur.append(carte_utilisateur);
        controlleur2=null
    } catch (err) {
        if (err.name === "AbortError") {
            console.log("Une requête Ajax a été annulée")
        } else {
            console.error("Erreur lors d'une requête Ajax");
            console.error(err);
            liste_utilisateur.textContent = "Erreur lors de la requête. Veuillez réessayer."
        }
    }
}

function initialisation() {
  liste_utilisateur = document.getElementById('liste_utilisateur')
  contenuInitial = liste_utilisateur.innerHTML;
  document.getElementById("courriel").addEventListener("input", rechercher_courriel);
  courriel = document.getElementById('courriel');
  btn_ajout.addEventListener('submit',ajouter);

}

window.addEventListener("load", initialisation);