"""Point d'entrée du pipeline de données du TP13."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from dataclasses import asdict, dataclass

import pandas as pd
from pyarrow.parquet import read_metadata

from src.cleaning import lire_brut
from src.cleaning import nettoyer as nettoyer_tp9
from src.etl_pipeline import extraire_brut
from src.storage.export_features import sha256
from src.report import generer_rapport

RACINE = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Configuration:
    source: Path
    dossier_donnees: Path
    date_execution: date


@dataclass(frozen=True)
class ResultatEtape:
    duree_s: float
    lignes: int
    fichiers: tuple[Path, ...]


def charger(config: Configuration) -> ResultatEtape:
    """Fige le CSV ou le Parquet source et produit son manifeste daté."""
    debut = perf_counter()
    source = config.source
    extension = source.suffix.lower()
    if extension not in {".csv", ".parquet"}:
        raise ValueError(f"Format source non pris en charge : {source.name}")

    dossier = config.dossier_donnees / "raw"
    copie = dossier / f"produits_bruts_{config.date_execution:%Y%m%d}{source.suffix}"
    chemin_manifeste = copie.with_suffix(f"{copie.suffix}.manifest.json")
    dossier.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(dir=dossier) as temporaire:
        copie_temporaire = Path(temporaire) / copie.name
        if copie.exists():
            instantane = copie
            empreinte = sha256(copie)
            if sha256(source) != empreinte:
                raise FileExistsError(f"L'instantané {copie} existe avec un contenu différent.")
        else:
            shutil.copyfile(source, copie_temporaire)
            instantane = copie_temporaire
            empreinte = sha256(instantane)

        if extension == ".csv":
            with instantane.open(encoding="utf-8-sig", newline="") as fichier:
                enregistrements = csv.reader(fichier)
                next(enregistrements, None)
                lignes = sum(1 for enregistrement in enregistrements if enregistrement)
        else:
            lignes = read_metadata(instantane).num_rows

        if instantane == copie_temporaire:
            # Publie la copie complète sans écraser une copie créée entre-temps.
            try:
                os.link(copie_temporaire, copie)
            except FileExistsError:
                if sha256(copie) != empreinte:
                    raise FileExistsError(f"L'instantané {copie} existe avec un contenu différent.") from None

        manifeste = {
            "statut": "termine",
            "chemin_source": str(source),
            "nom_copie": copie.name,
            "date": config.date_execution.isoformat(),
            "SHA_256": empreinte,
        }
        manifeste_temporaire = Path(temporaire) / chemin_manifeste.name
        with manifeste_temporaire.open("w", encoding="utf-8") as fichier:
            json.dump(manifeste, fichier, indent=4, ensure_ascii=False)
        os.replace(manifeste_temporaire, chemin_manifeste)

    return ResultatEtape(perf_counter() - debut, lignes, (copie, chemin_manifeste))



def nettoyer(config: Configuration) -> ResultatEtape:
    """Produit le jeu nettoyé commun et les traces du nettoyage TP9."""
    debut = perf_counter()
    date_demandee = f"{config.date_execution:%Y%m%d}"
    dossier_brut = config.dossier_donnees / "raw"
    extension = config.source.suffix.lower()

    if extension not in {".csv", ".parquet"}:
        raise ValueError(f"Format du brut non pris en charge : {extension}")

    # TODO 1 — Retrouver un instantané et vérifier son intégrité.
    candidats = []
    for fichier in dossier_brut.glob("produits_bruts_????????.*"):
        if fichier.suffix.lower() != extension or not fichier.is_file():
            continue

        chemin_manifeste = fichier.with_suffix(f"{fichier.suffix}.manifest.json")
        if chemin_manifeste.is_file():
            candidats.append((fichier, chemin_manifeste))

    if not candidats:
        raise FileNotFoundError(
            f"Aucun brut {extension} avec manifeste dans {dossier_brut}. "
            "Lance d'abord l'étape charger."
        )

    nom_demande = f"produits_bruts_{date_demandee}"
    brut, chemin_manifeste = max(
        candidats,
        key=lambda candidat: (
            candidat[0].stem == nom_demande,
            candidat[0].stem,
        ),
    )

    with chemin_manifeste.open(encoding="utf-8") as fichier:
        manifeste = json.load(fichier)

    if manifeste.get("SHA_256") != sha256(brut):
        raise ValueError(f"L'empreinte du brut ne correspond pas au manifeste : {brut}")

    # TODO 2 — Préparer le DataFrame d'entrée, puis appliquer le TP9.
    if extension == ".csv":
        df_brut = lire_brut(brut)
        if "food_groups_tags" not in df_brut.columns:
            df_brut["food_groups_tags"] = None
    else:
        colonnes = set(read_metadata(brut).schema.to_arrow_schema().names)
        if {"countries_tags", "nutriments"} & colonnes:
            destination = (
                config.dossier_donnees / "extracts" / f"france_{brut.stem}.parquet"
            )
            df_brut = extraire_brut(brut, destination)
        else:
            df_brut = pd.read_parquet(brut)

    manquantes = {"code", "food_groups_tags"}.difference(df_brut.columns)
    if manquantes:
        raise ValueError(f"Colonnes manquantes dans {brut.name} : {sorted(manquantes)}")

    propre, journal = nettoyer_tp9(df_brut)

    # TODO 3 — Écrire les trois sorties datées et retourner le résultat.
    dossier_clean = config.dossier_donnees / "clean"
    dossier_clean.mkdir(parents=True, exist_ok=True)

    chemin_propre = dossier_clean / f"produits_propres_{date_demandee}.parquet"
    chemin_rapport = dossier_clean / f"rapport_nettoyage_{date_demandee}.md"
    chemin_journal = dossier_clean / f"journal_regles_{date_demandee}.json"

    propre.to_parquet(chemin_propre, index=False)

    generer_rapport(
        df_brut,
        propre,
        journal,
        chemin_rapport,
        source=str(brut),
        jour=config.date_execution,
    )

    with chemin_journal.open("w", encoding="utf-8") as fichier:
        json.dump([asdict(regle) for regle in journal], fichier, ensure_ascii=False, indent=2)
        fichier.write("\n")

    return ResultatEtape(
        duree_s=perf_counter() - debut,
        lignes=len(propre),
        fichiers=(chemin_propre, chemin_rapport, chemin_journal),
    )


def charger_base(config: Configuration) -> ResultatEtape:
    """Charge PostgreSQL depuis le jeu nettoyé commun et lance les contrôles."""
    # TODO 1 — Résoudre le même produits_propres_<AAAAMMJJ>.parquet que parquet.
    # Préfère la date demandée, puis le plus récent. En l'absence de fichier,
    # indique de lancer nettoyer. Lis le Parquet puis appelle vers_tables_sql()
    # de src.etl_pipeline pour construire les cinq tables d'import.
    #
    # TODO 2 — Raccorder les contrôles et insertions existants à ces tables.
    # Utilise src/load_database.py comme référence pour l'ordre des insertions.
    # Son main() refait le nettoyage et clear_database() tronque via une autre
    # connexion. Les fonctions insert_* lisent des fichiers depuis INPUT_DIR.
    # Fais évoluer ces interfaces pour recevoir les fichiers d'import de ce run
    # et utilise une base de test dédiée. Vérifie les fichiers et l'unicité des
    # codes avant l'écriture. Exécute le remplacement et les insertions dans une
    # même transaction PostgreSQL afin qu'un échec permette un rollback complet.
    #
    # TODO 3 — Contrôler le résultat et retourner la durée et le nombre de produits.
    # final_check() affiche des totaux. Récupère aussi le COUNT de products
    # pour vérifier qu'il est égal à len(propre). Retourne les chemins réellement
    # produits, par exemple un rapport de contrôle daté sous db/ si tu en écris un.
    # Contrôle — Enchaîne deux imports du même extrait dans la base de test.
    # Compare les effectifs et les codes, puis provoque un échec pendant l'import
    # et vérifie que le contenu validé avant cet échec est toujours disponible.
    raise NotImplementedError("L'étape charger_base reste à implémenter.")


def parquet(config: Configuration) -> ResultatEtape:
    """Convertit le jeu nettoyé commun en Parquet partitionné."""
    # TODO 1 — Résoudre le Parquet nettoyé commun sous clean/, avec la même
    # règle date demandée puis plus récent que charger_base. En cas d'absence,
    # indique de lancer nettoyer. Lis le DataFrame propre, puis passe-le à
    # src.storage.preparer_csv.preparer() et écris le CSV intermédiaire attendu
    # par convertir(). Cette projection ajoute le rayon à partir du nettoyé.
    #
    # TODO 2 — Produire les partitions et leur schéma sous parquet/produits_<AAAAMMJJ>.
    # Appelle convertir(csv_chemin, dossier_temporaire, schema_chemin) depuis
    # src.storage.convert_parquet. Choisis un sous-dossier temporaire dédié,
    # car convertir() efface et recrée sa destination. Place le schéma dans ce
    # dossier pour publier les partitions et leur schéma ensemble.
    # Compare le nombre de lignes retourné à celui du nettoyé. Une fois la sortie
    # contrôlée, crée _SUCCESS en dernier et publie le dossier complet. Si une
    # sortie datée existe déjà, conserve-la tant que le remplacement n'est pas prêt.
    # Retourne la durée, le nombre de lignes et les sorties publiées.
    # Contrôle — Vérifie les dossiers rayon=..., les types et les effectifs.
    # Une conversion interrompue doit laisser la sortie précédente utilisable.
    raise NotImplementedError("L'étape parquet reste à implémenter.")


def exports(config: Configuration) -> ResultatEtape:
    """Produit l'export ML daté et son schéma à partir du Parquet complet."""
    # TODO 1 — Chercher sous parquet/ le dossier de la date demandée, puis le
    # plus récent. Ne retiens que les dossiers avec _SUCCESS, leur schéma et des
    # partitions. Si aucun dossier complet n'existe, indique de lancer parquet.
    #
    # TODO 2 — Appeler src.storage.export_features.exporter() avec le dossier
    # retenu, <dossier_donnees>/exports et config.date_execution. L'exporteur
    # gère le split stratifié sur le grade, la graine 42 et le refus d'écrasement.
    # Garde force=False tant qu'aucune option explicite n'a été demandée.
    # Retrouve le schéma avec chemin_schema(), lis son champ lignes et retourne
    # la durée, ce nombre de produits et les chemins du Parquet et du JSON.
    # Contrôle — Compare les affectations train/test par code sur deux exports
    # isolés du même jeu et vérifie qu'un rejeu ne remplace pas un export figé.
    raise NotImplementedError("L'étape exports reste à implémenter.")


ETAPES = {
    "charger": charger,
    "nettoyer": nettoyer,
    "charger_base": charger_base,
    "parquet": parquet,
    "exports": exports,
}


def executer(etape: str, config: Configuration) -> None:
    """Exécute une étape choisie ou le pipeline complet."""
    if etape == "all":
        # TODO — Définir l'ordre de all avec les étapes déclarées dans ETAPES.
        # Lance charger, nettoyer, charger_base, parquet, puis exports avec la même
        # Configuration. Réutilise le chemin d'exécution d'une étape seule pour
        # bénéficier du même affichage et du même journal. Arrête au premier échec.
        # Contrôle — Avec des fonctions factices, vérifie l'ordre puis fais lever
        # une exception à nettoyer et vérifie qu'aucune étape suivante n'est appelée.
        raise NotImplementedError("L'orchestration complète reste à implémenter.")

    resultat = ETAPES[etape](config)
    # TODO — Encadrer l'appel ETAPES[etape](config) pour journaliser succès et échec.
    # Sous <dossier_donnees>/logs, ajoute une ligne JSONL par exécution d'étape.
    # Note l'horodatage réel, la date des données, l'étape, la durée et le statut.
    # En cas de succès, ajoute lignes et fichiers depuis ResultatEtape, avec les
    # chemins convertis en chaînes. En cas d'échec, mesure quand même la durée,
    # ajoute le message d'erreur, puis propage l'exception à l'appelant.
    # Contrôle — Provoque un succès puis un échec avec des fonctions factices.
    # Vérifie que les deux entrées JSON sont lisibles et que l'échec se propage.
    print(f"{etape} : {resultat.lignes} lignes en {resultat.duree_s:.2f} s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("etape", choices=[*ETAPES, "all"], help="Étape à exécuter ou all pour le flux complet")
    parser.add_argument(
        "--source",
        type=Path,
        default=os.environ.get("NUTRISCOPE_SOURCE", "data/food.parquet"),
        help="CSV ou Parquet source. Prioritaire sur NUTRISCOPE_SOURCE.",
    )
    parser.add_argument("--dossier-donnees", type=Path, default=Path("data"), help="Dossier des sorties")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today(), help="Date des sorties (AAAA-MM-JJ)")
    args = parser.parse_args()

    config = Configuration(
        source=(RACINE / args.source).resolve(),
        dossier_donnees=(RACINE / args.dossier_donnees).resolve(),
        date_execution=args.date,
    )
    try:
        executer(args.etape, config)
    except (NotImplementedError, ValueError, OSError) as erreur:
        parser.exit(1, f"Erreur : {erreur}\n")


if __name__ == "__main__":
    main()
