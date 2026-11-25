console.log("FICHIER JAVASCRIPT CHARGÉ");

"use strict"

const nomCarte = document.getElementById("recherche_carte");
const message_erreur = document.getElementById("msg_erreur_carte");
const formulaire = document.getElementById("formRecherche");

formulaire.addEventListener("submit", async function (event) {
    
    event.preventDefault();

    message_erreur.textContent="";
    nomCarte.classList.remove("is-invalid");

    const aRechercher = nomCarte.value.trim()
    const controleur = new AbortController()

    const parametres = {
        "nom_carte" : aRechercher
    }

    try{
        const resultats = await envoyerRequeteAjax(
            "/api/page_collection",
            "GET",
            parametres,          
        )
        console.log(resultats);
    }
    catch (erreur){
        console.error(erreur);
        message_erreur.textContent = erreur.resultat?.msg_erreur_carte || erreur.message;

        nomCarte.classList.add("is-invalid")
    }  
});


