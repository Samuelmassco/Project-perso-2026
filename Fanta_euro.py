"""
Script de gestion du Fanta Euro - Calcul des scores des pronosticateurs
Charge les pronostics depuis fanta.csv, les compare avec les bonnes réponses,
et génère un classement des joueurs.
"""

import pandas as pd
import os
from pathlib import Path


# Bonnes réponses pour les matchs de l'Euro
# Format: 'X' pour match nul, '1' pour victoire de l'équipe à domicile, '2' pour victoire de l'équipe en déplacement
BONNES_REPONSES = {
    'ESPAGNE-SERBIE': '1',#groupe Espagne Allemagne Serbie Autriche
    'ALLEMAGNE AUTRICHE': '1',
    'Autriche-Espagne': '2',
    'Serbie - Allemagne': '1',
    'Autriche - Serbie': '0',
    'Allemagne - Espagne': '0',
    'Portugal-Roumanie': '1',#groupe Portugal Macédoine du Nord Danemark Roumanie
    'Danemark Macédoine du Nord': '1',
    'Macédoine du Nord - Portugal': '0',
    'Roumanie - Danemark': '0',
    'Macédoine du Nord - Roumanie': '0',
    'Danemark - Portugal': '0',
    'France - Rép. Tchèque': '1',#groupe France Rép. Tchèque Norvège Ukraine
    'Norvège - Ukraine': '1',
    'Ukraine-  France': '2',
    'Rép. Tchèque Norvège': '2',
    'Rép. Tchèque - Ukraine': '0',
    'France - Norvège': '0',
    'Slovénie - Monténégro': '1',#groupe Monténégro Iles Féroé Slovénie Suisse
    'Iles Féroé - Suisse': 'x',
    'Monténégro - Iles Féroé': '0',
    'Suisse - Slovénie': '0',
    'Monténégro - Suisse': '0',
    'Slovénie - Iles Féroé': '0',
    'Croatie - Géorgie': '1',#groupe Croatie Pays-Bas Géorgie Suède
    'Suède - Pays-Bas': '1',
    'Pays-Bas - Croatie': '0',
    'Géorgie - Suède': '0',
    'Pays-Bas - Géorgie': '0',
    'Suède - Croatie': '0',
    'Islande - Italie': '1',#groupe ISlande Italie Hongrie Pologne
    'Hongrie - Pologne': '1',
    'Pologne - Islande': '0',
    'Italie - Hongrie': '0',
    'Pologne - Italie': '0',
    'Hongrie - Islande': '0',
}


def charger_donnees(file_path=None):
    """
    Charge les données depuis le fichier CSV.
    
    Args:
        file_path (str): Chemin vers le fichier CSV (optionnel)
        
    Returns:
        pd.DataFrame: DataFrame contenant les données
    """
    try:
        # Si pas de chemin spécifié, utiliser le chemin relatif au script
        if file_path is None:
            script_dir = Path(__file__).parent
            file_path = script_dir / 'CSHB_Prono.csv'
        
        df = pd.read_csv(file_path)
        print(f"✓ Fichier '{file_path}' chargé avec succès")
        print(f"  - {len(df)} participations")
        print(f"  - {len(df.columns)} colonnes\n")
        return df
    except FileNotFoundError:
        print(f"✗ Erreur : Le fichier '{file_path}' n'existe pas.")
        return None
    except Exception as e:
        print(f"✗ Erreur lors de la lecture du fichier : {e}")
        return None


def calculer_score(row, match_columns, bonnes_reponses):
    """
    Calcule le score d'un joueur en comparant ses pronostics avec les bonnes réponses.
    
    Args:
        row (pd.Series): Ligne contenant les pronostics d'un joueur
        match_columns (list): Liste des colonnes représentant les matchs
        bonnes_reponses (dict): Dictionnaire des bonnes réponses
        
    Returns:
        int: Score du joueur
    """
    score = 0
    for match in match_columns:
        if match in row.index and match in bonnes_reponses:
            pronostic = str(row[match]).strip().upper()
            bonne_reponse = str(bonnes_reponses[match]).strip().upper()
            
            if pronostic == bonne_reponse:
                score += 1
    
    return score


def generer_classement(df_original, bonnes_reponses=BONNES_REPONSES):
    """
    Génère un classement des joueurs basé sur leurs scores.
    
    Args:
        df_original (pd.DataFrame): DataFrame contenant les données originales
        bonnes_reponses (dict): Dictionnaire des bonnes réponses
        
    Returns:
        pd.DataFrame: DataFrame du classement
    """
    # Liste des colonnes représentant les matchs
    match_columns = list(bonnes_reponses.keys())
    
    # Créer un DataFrame pour stocker les résultats avec surnom, score et collectif
    df_scores = pd.DataFrame()
    
    # Ajouter le surnom
    if 'surnom' in df_original.columns:
        df_scores['Surnom'] = df_original['surnom']
    else:
        df_scores['Surnom'] = df_original.get('Adresse e-mail', df_original.get('email', ''))
    
    # Ajouter le score
    df_scores['Score'] = df_original.apply(
        lambda row: calculer_score(row, match_columns, bonnes_reponses), 
        axis=1
    )
    
    # Ajouter le collectif
    if 'collectif ' in df_original.columns:
        df_scores['Collectif'] = df_original['collectif ']
    
    # Trier par score décroissant
    df_classement = df_scores.sort_values(
        by='Score', 
        ascending=False
    ).reset_index(drop=True)
    
    # Ajouter le rang
    df_classement.insert(0, 'Rang', range(1, len(df_classement) + 1))
    
    return df_classement


def afficher_classement(df_classement):
    """
    Affiche le classement de manière lisible.
    
    Args:
        df_classement (pd.DataFrame): DataFrame du classement
    """
    print("=" * 70)
    print("CLASSEMENT FANTA EURO".center(70))
    print("=" * 70)
    print(df_classement.to_string(index=False))
    print("=" * 70)


def sauvegarder_classement(df_classement, output_path='classement_fanta_euro.csv'):
    """
    Sauvegarde le classement dans un fichier CSV.
    
    Args:
        df_classement (pd.DataFrame): DataFrame du classement
        output_path (str): Chemin du fichier de sortie
    """
    try:
        df_classement.to_csv(output_path, index=False)
        print(f"\n✓ Classement sauvegardé : {output_path}")
    except Exception as e:
        print(f"\n✗ Erreur lors de la sauvegarde : {e}")


def main():
    """Fonction principale."""
    print("\n" + "=" * 70)
    print("ANALYSEUR DE PRONOSTICS - FANTA EURO".center(70))
    print("=" * 70 + "\n")
    
    # Charger les données
    df = charger_donnees()
    if df is None:
        return
    
    # Générer le classement
    df_classement = generer_classement(df)
    
    # Afficher le classement
    afficher_classement(df_classement)
    
    # Sauvegarder le classement
    sauvegarder_classement(df_classement)
    
    # Statistiques
    print(f"\nScore maximum : {df_classement['Score'].max()}")
    print(f"Score minimum : {df_classement['Score'].min()}")
    print(f"Score moyen : {df_classement['Score'].mean():.2f}")


if __name__ == "__main__":
    main()