# NutriScope — état des lieux et tickets proposés

Audit du 25 novembre 2026. Référence intégrée du fork : `develop` à `3400560`. Lecture statique des branches et comparaison avec l’audit historique du 23 novembre. Aucun test ni chargement rejoué pour cet inventaire.

Sources : `docs/Cahier_TP_NutriScope.md`, `docs/tps/`, refs Git locales et rapport `reports/audit_tp21_2026-11-23/avancement_tp.csv` au commit `b87ed26`.

Pour la suite, les dépendances directes de l’assistant multi-tours sont la substitution TP16, la recherche produit TP18 et les réponses sourcées TP19. Le TP20 mesure leur qualité et le TP22 prépare le gel. Le chantier API et démo vient en aval.

## [TP 1–3] Tracer le socle du dépôt et du périmètre Open Food Facts

Les notebooks de démarrage et de profilage, le périmètre produit et les règles de contribution sont versionnés dans develop.

- [ ] Rejouer les notebooks sur le périmètre documenté et conserver les sorties utiles. Vérifier le guide de démarrage et le parcours de revue sur le fork.

## [TP 4] Valider la base produits PostgreSQL

Le schéma SQL, les requêtes de contrôle et le chargeur sont intégrés.

- [ ] Rejouer le chargement sur une base isolée, comparer les contrôles et vérifier le comportement en cas d’échec partiel.

## [TP 5–8] Consolider le cadrage produit

Personas, benchmark, KPI et hypothèses figurent dans docs/cadrage.

- [ ] Rassembler la note de cadrage, les décisions de périmètre, le planning et les hypothèses de coûts validées.

## [TP 9–12] Tracer le socle de préparation et d’analyse des données

Nettoyage, EDA, support de datastorytelling et stockage Parquet/DuckDB sont intégrés. Les résultats de tests de l’audit du 23/11 sont historiques.

- [ ] Référencer les livrables et résultats, vérifier le rejeu sur échantillon et consigner les validations du jalon J3.

## [TP 13] Achever le pipeline de données rejouable

Le split stratifié est intégré (e02d648). Un notebook de travail existe à 8bd221a, et le guide CLI à 2caaa2c.

- [ ] Fournir une commande de bout en bout, des étapes idempotentes, la documentation et un rejeu sur machine vierge avec le jalon v0.3.

## [TP 14] Évaluer un modèle de prédiction du Nutri-Score

La branche TP14 contient la préparation et les contrats de test à 9320531. L’audit relève un module de modélisation manquant.

- [ ] Comparer les baselines et un pipeline entraîné sur le split figé, vérifier les fuites, mesurer les performances et analyser les erreurs.

## [TP 15] Comparer les méthodes d’ensemble

Le sujet détaillé est versionné. Aucune implémentation spécifique repérée dans les branches auditées.

- [ ] Après TP14, comparer le boosting aux baselines sur le même protocole, puis retenir un modèle dans une ADR avec ses limites.

## [TP 16] Implémenter la segmentation et la substitution nutritionnelle

Le support de segmentation dans docs/tps/tp16 est un notebook d’exercice. Aucun moteur intégré repéré.

- [ ] Évaluer la segmentation et produire des substituts explicables par sous-catégorie, avec variantes bio et cas sans candidat. Exposer un contrat testable pour TP21.

## [TP 17] Intégrer le classifieur d’images par rayon

Sur le fork, d9a3999 apporte le téléchargement des images. L’audit du 23/11 référence une évaluation sur une branche d’équipe.

- [ ] Identifier les artefacts réutilisables, reproduire l’évaluation sur test séparé, documenter le seuil de rejet et intégrer sur le fork.

## [Atelier scanner] Valider le scanner d’étiquettes

Prototype, notebook et outils de mesure présents sur la branche locale Klement/feat/tp_scanner à 59abadf. Voir docs/tps/tp16/README_tp_16-11.md.

- [ ] Rejouer les paliers sur le lot annoté, enregistrer les erreurs et la latence et préparer le raccordement au parcours produit.

## [TP 18] Consolider la recherche produit outillée

Le notebook d’appel `chercher_produit` est intégré via la PR #1. Une autre implémentation existe sur la branche TP19.

- [ ] Retenir un contrat commun, tester les cas produit inconnu et score manquant, puis versionner l’ADR et le schéma d’architecture.

## [TP 19] Sourcer les réponses avec le RAG

À f5960b7, ingestion et retrieval sont en place sur un lot de fiches. Le sujet détaillé est dans le kit docs/tps/tp19.

- [ ] Compléter le corpus documentaire et les licences, vérifier l’ingestion rejouable et la mise à jour des métadonnées, livrer `repondre_source` avec citations et refus si preuves insuffisantes.

## [TP 20] Mesurer et améliorer la qualité du RAG

À f5960b7, un jeu de 30 questions est prévu et les résultats enregistrés portent sur 14 cas produits/comparaisons.

- [ ] Mesurer hit rate et MRR, évaluer exactitude, fidélité et refus sur les 30 cas, comparer deux itérations sur le même jeu.

## [TP 21] Orchestrer les trois outils en conversation

Le notebook à 1a8c41b contient un premier travail LangChain et des TODO pour l’historique, la substitution, la réponse sourcée et la journalisation.

- [ ] Brancher les outils TP16/18/19, rejouer les scénarios multi-tours, tracer outil, latence et jetons, puis documenter la revue croisée.

## [TP 22] Valider les garde-fous et geler l’assistant v1

Le prototype comporte des consignes de périmètre. Le rapport de validation et le gel restent à produire.

- [ ] Versionner le prompt et les refus, automatiser les régressions issues des tests croisés, documenter la décision de fine-tuning et publier v0.5.

## [TP 23] Exposer les fonctionnalités via FastAPI

Travail prévu après l’intégration des briques produit et assistant.

- [ ] Livrer les quatre routes produit, score, substituts et assistant, des schémas Pydantic, une documentation OpenAPI, des tests et des mesures de latence.

## [TP 24] Livrer l’application de démonstration

Travail prévu, dépendant de l’API TP23.

- [ ] Couvrir recherche produit, score, substituts et discussion via l’API, avec états de chargement et d’erreur, guide et démo croisée.

## [TP 25] Conteneuriser NutriScope

Travail prévu après API et interface.

- [ ] Fournir les images et un Compose pour API, interface et bases, avec configuration d’exemple, persistance et démarrage validé sur machine vierge.

## [TP 26] Automatiser la CI/CD vers la préproduction

Le checkout actuel contient des manifestes locaux non suivis. Aucun workflow complet observé sur develop.

- [ ] Faire tourner lint et tests, publier les images versionnées et prouver un déploiement automatique en préproduction.

## [TP 27] Déployer NutriScope en HTTPS

Travail prévu après le pipeline de préproduction.

- [ ] Déployer via CI, documenter migrations, variables, sauvegardes et journaux, vérifier le parcours complet depuis un réseau externe.

## [TP 28] Stabiliser et publier NutriScope v1.0

Travail prévu après le déploiement.

- [ ] Trier le backlog de stabilisation, réaliser la revue croisée, corriger les points bloquants et publier le tag et le rapport v1.0.

## [TP 29] Superviser l’application et la qualité des modèles

Travail prévu après le déploiement. La journalisation du TP21 constitue un prérequis.

- [ ] Livrer healthchecks, alertes, journaux structurés, tableau de bord et rejeu planifié des évaluations RAG et Nutri-Score.

## [TP 30–31] Préparer la démonstration et le dossier de certification

Travail prévu après stabilisation. La documentation existante alimente le dossier.

- [ ] Valider le guide d’installation, préparer la démo et son plan hors ligne, tracer les retours de soutenance, lier les preuves BC01 à BC05 et geler la v1.1.
