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

from pyarrow.parquet import read_metadata

from src.storage.export_features import sha256

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
                raise FileExistsError(f"L’instantané {copie} existe avec un contenu différent.")
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
                    raise FileExistsError(f"L’instantané {copie} existe avec un contenu différent.") from None

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
    """Produit le jeu nettoyé commun et le rapport de nettoyage du TP9."""
    # TODO : retrouver le brut figé et appeler les fonctions existantes du TP9.
    raise NotImplementedError("L'étape nettoyer reste à implémenter.")


def charger_base(config: Configuration) -> ResultatEtape:
    """Charge PostgreSQL depuis le jeu nettoyé commun et lance les contrôles."""
    # TODO : raccorder le chargeur existant au nettoyé et garantir un rejeu sans doublon.
    raise NotImplementedError("L'étape charger_base reste à implémenter.")


def parquet(config: Configuration) -> ResultatEtape:
    """Convertit le jeu nettoyé commun en Parquet partitionné."""
    # TODO : appeler la conversion du TP12 et signaler la fin de l'écriture.
    raise NotImplementedError("L'étape parquet reste à implémenter.")


def exports(config: Configuration) -> ResultatEtape:
    """Produit l'export ML daté et son schéma à partir du Parquet complet."""
    # TODO : retrouver un Parquet complet et réutiliser l'export avec son split figé.
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
        # TODO : enchaîner les étapes selon leurs dépendances et arrêter au premier échec.
        raise NotImplementedError("L'orchestration complète reste à implémenter.")

    resultat = ETAPES[etape](config)
    # TODO : journaliser les succès et les échecs, pour une étape seule comme pour all.
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
