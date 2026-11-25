"use strict";

let nom_pokemon = null;
let controleur = null;
let liste_pokemon = null;
let contenuInitial = null;
function gererClickFenetre(evenement){
    const clickDansInput = nom_pokemon.contains(evenement.target);

    console.log("Clic dans la zone cliquable ? " + clickDansInput);

    if (!clickDansInput) {
        document.removeEventListener("click",rechercher)
    }
}

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


function creerLigne(texte) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = texte;
    return li;
}

function creerBouton(texte, url) {
    const lien = document.createElement("a");
    lien.href = url;
    lien.className = "btn btn-primary btn-sm mt-1 mb-1 rounded-pill";
    lien.textContent = texte;
    return lien;
}

function creerCarte(p,peut_faire_offre) {
    const carte = document.createElement("div");
    carte.className = "card";
    carte.style.width = "17rem";

    const img = document.createElement("img");
    img.src = p.photo;
    img.className = "card-img-top";
    img.alt = "Image Pokemon";
    carte.append(img);

    const corps = document.createElement("div");
    corps.className = "card-body";
    const titre = document.createElement("h5");
    titre.className = "card-title";
    titre.textContent = p.name;
    corps.append(titre);
    carte.append(corps);

    const liste = document.createElement("ul");
    liste.className = "list-group list-group-flush";

    if (p.types != null) {
        const types = p.types.replace(/[\[\]']/g, "");
        liste.append(creerLigne("Type : " + types));
    }
    if (p.set_num != null) liste.append(creerLigne("Valeur : " + p.set_num));
    if (p.rarity != null) liste.append(creerLigne("Rareté : " + p.rarity));
    if (p.condition != null) liste.append(creerLigne("Condition : " + p.condition));
    if (p.cost != null) liste.append(creerLigne("Coût : " + p.cost));
    if (p.status != null) liste.append(creerLigne("Status : " + p.status));
    carte.append(liste);

    const boutons = document.createElement("div");
    boutons.className = "d-flex justify-content-center align-items-center gap-3";
    boutons.append(creerBouton("Afficher les détails", `/collection/detail/${p.id}`));
    carte.append(boutons);

    if(peut_faire_offre ===true){
        boutons.append(creerBouton("Faire une offre ", `/collection/ajout_offre/${p.id}`));
    }
    carte.append(boutons);  

    return carte;
}

async function rechercher() {
    const achercher = nom_pokemon.value.trim();
    if (controleur != null) {
        controleur.abort();
    }

    if(achercher.length <3){
        liste_pokemon.innerHTML = contenuInitial
        return;
    }
    controleur = new AbortController()

    const parametres = {
    "nom_pokemon": achercher,
    }
    try {
        const resultat = await envoyerRequeteAjax(
        "/api/recherche",
        "GET",
        parametres, 
        controleur     
        );
        
        liste_pokemon.textContent="";
        if (resultat.pokemon.length===0) {
            const messsage='Aucun résultat  🥀'
            const div= afficher_erreur(messsage)
            liste_pokemon.append(div);
            return;
        }

        resultat.pokemon.forEach(pokemon => {
            const carte = creerCarte(pokemon,resultat.peut_faire_offre);
            liste_pokemon.append(carte);
        });
    } catch (err) {
        if (err.name === "AbortError") {
            console.log("Une requête Ajax a été annulée")
        } else {
            console.error("Erreur lors d'une requête Ajax");
            console.error(err);
            liste_pokemon.textContent = "Erreur lors de la requête. Veuillez réessayer."
        }
    }
    document.addEventListener('click',gererClickFenetre)
}


function initialisation() {
  liste_pokemon = document.getElementById('liste-pokemon')
  contenuInitial = liste_pokemon.innerHTML;
  nom_pokemon = document.getElementById('nom_pokemon');
  document.getElementById("nom_pokemon").addEventListener("input", rechercher);
  document.getElementById("nom_pokemon").addEventListener("submit", rechercher);
}

window.addEventListener("load", initialisation);