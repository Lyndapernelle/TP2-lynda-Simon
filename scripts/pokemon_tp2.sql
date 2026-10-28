CREATE TABLE `collectionneurs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `courriel` VARCHAR(150) NOT NULL,
  `mot_de_passe` VARCHAR(255) NOT NULL,
  `credit` DECIMAL(10,0) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  CONSTRAINT `uk_collectionneur_courriel` UNIQUE (`courriel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- vider le contenu de elements_collection avant d'ajouter la contrainte de clé étrangère.
DELETE FROM `elements_collection`;


ALTER TABLE `elements_collection`
  ADD COLUMN `id_collectionneur` INT(10) UNSIGNED NOT NULL AFTER `id`,
  ADD CONSTRAINT `fk_elements_collectionneur` 
    FOREIGN KEY (`id_collectionneur`) REFERENCES `collectionneurs` (`id`)

CREATE TABLE `offres` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_elem_collection` INT(10) UNSIGNED NOT NULL,
  `id_collectionneur` INT UNSIGNED NOT NULL,
  `prix_offert` DECIMAL(10,0) NOT NULL,
  `date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `statut` ENUM('en attente', 'acceptée', 'refusée') NOT NULL DEFAULT 'en attente',
  PRIMARY KEY (`id`),
  CONSTRAINT `uk_offres_composite` UNIQUE (`id_elem_collection`, `id_collectionneur`, `date`),
  CONSTRAINT `fk_offres_element` FOREIGN KEY (`id_elem_collection`) REFERENCES `elements_collection` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_offres_collectionneur` FOREIGN KEY (`id_collectionneur`) REFERENCES `collectionneurs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

 
CREATE OR REPLACE TABLE inscription_bulletin(
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `courriel` VARCHAR(50) UNIQUE,
  `frequence` ENUM('quotidien','hebdomadaire','mensuel') UNSIGNED NOT NULL,
  `annulee` tinyint(1)
)