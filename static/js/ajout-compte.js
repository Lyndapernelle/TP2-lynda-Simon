"use strict"

const courriel_utilisateur = document.getElementsById("courriel_utilisateur");
const mdp_utilisateur = document.getElementById("mdp");
const msg_erreur_courriel = document.getElementsById("message_courriel");
const formulaire = document.getElementById("formCompte");


formulaire.addEventListener("submit", async function ajout_compte (event) {
    
    event.preventDefault();
   
    message_erreur_courriel.textContent="";
    courriel_utilisateur.classList.remove("is-invalid");

    const controleur = new AbortController()
    
    const parametres = {
        "courriel" : courriel_utilisateur.trim(),
        "mot_de_passe" : mdp_utilisateur.trim()
    }
    try{
        const resultats = await envoyerRequeteAjax(
            "/api/creer-compte-rapide",
            "GET",
            parametres,
            controleur     
        )

    }
    catch (erreur){
        console.error(erreur);
        msg_erreur_courriel.textContent = erreur.resultat?.msg_erreur_courriel|| erreur.message;

        courriel_utilisateur.classList.add("is-invalid")
    }  
});

