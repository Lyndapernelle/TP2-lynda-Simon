"use strict"

const courriel_utilisateur = document.getElementsById("recherche_utilisateur");
const message_erreur = document.getElementById("msg_erreur_courriel");
const formulaire = document.getElementById("formRecherche");


formulaire.addEventListener("submit", async function charger_utilisateur (event) {

    event.preventDefault();

    message_erreur.textContent="";
    courriel_utilisateur.classList.remove("is-invalid");

    const aRechercher = courriel_utilisateur.value.trim()
    const controleur = new AbortController()

    const parametres = {
        "courriel" : aRechercher
    }
    try{
        const resultats = await envoyerRequeteAjax(
            "/api/liste_utilisateur",
            "GET",
            parametres,
            controleur
        )
        afficher_resultat(resultats.resultat)
    }
    catch (erreur){
        console.error(erreur);
        message_erreur.textContent = erreur.resultat?.msg_erreur_courriel || erreur.message;

        courriel_utilisateur.classList.add("is-invalid")
    }  
});

function afficher_resultat(resultats){
    resultats.forEach(resultat => {
        
    });
}
