import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import statsmodels.formula.api as smf
import requests
import os
import py7zr
from shapely.geometry import Point

# Configuration initiale
REPERTOIRE_ENTREE = "../input"
REPERTOIRE_SORTIE = "../output"
PERIODES = [1968, 1999, 2021]  # Garder les années utilisées dans l'original

def preparer_donnees_emploi(chemin_fichier="../input/pop-act2554-empl-csp-cd-trav-6821_lieu-travail.xlsx"):
    """Préparation des données d'emploi pour différentes années"""
    donnees_par_annee = {}
    fichier_excel = pd.ExcelFile(chemin_fichier)
    
    for annee in PERIODES:
        # Chargement du DataFrame pour chaque année
        df = pd.read_excel(fichier_excel, f'COM_{annee}', skiprows=13)
        
        # Suppression des lignes non pertinentes
        df = df[df['Région \nen géographie courante'] != 'RLT']
        
        # Calcul du total des emplois
        df[f'Total_Emploi_{annee}'] = (
            df[f"Agriculteurs\nRP{annee}"] + 
            df[f"Artisans, commerçants, chefs d'entreprises\nRP{annee}"] +
            df[f"Cadres et professions intellectuelles supérieures\nRP{annee}"] +
            df[f"Professions intermédiaires\nRP{annee}"] + 
            df[f"Employés\nRP{annee}"] +
            df[f"Ouvriers\nRP{annee}"]
        )
        
        # Création du code INSEE
        df['code'] = (
            df["Département\nen géographie courante"].astype(str).str.zfill(2) + 
            df["Commune\nen géographie courante"].astype(str).str.zfill(3)
        )
        
        donnees_par_annee[annee] = df
    
    return donnees_par_annee

def filtrer_agglomeration(donnees_emploi, donnees_zones_urbaines):
    """Filtrage des données pour les agglomérations de Paris et Lyon"""
    # Chargement des zones urbaines
    zones_urbaines = pd.read_excel(donnees_zones_urbaines, 'Composition_communale', skiprows=5)
    
    # Filtrage pour Lyon et Paris
    zones_lyon = zones_urbaines[zones_urbaines['AU2010'] == '002']
    zones_paris = zones_urbaines[zones_urbaines['AU2010'] == '001']
    
    # Préparation des codes
    zones_lyon['code'] = zones_lyon['CODGEO'].astype(str).str.zfill(5)
    zones_paris['code'] = zones_paris['CODGEO'].astype(str).str.zfill(5)
    
    # Données de base de 1968
    donnees_finales = donnees_emploi[1968].copy()
    
    # Ajout des données pour 1999 et 2021
    for annee in [1999, 2021]:
        donnees_finales[f'Total_Emploi_{annee}'] = donnees_emploi[annee][f'Total_Emploi_{annee}']
    
    # Filtrage par agglomération
    paris_df = donnees_finales.merge(zones_paris[['code']], on='code', how='inner')
    lyon_df = donnees_finales.merge(zones_lyon[['code']], on='code', how='inner')
    
    # Ajout des arrondissements de Paris
    arrondissements_paris = donnees_finales[donnees_finales['code'].str.startswith('751')]
    paris_df = pd.concat([paris_df, arrondissements_paris], ignore_index=True)
    
    return paris_df, lyon_df

def charger_donnees_geographiques(url_carte, dossier_extraction):
    """Téléchargement et extraction des données cartographiques"""
    os.makedirs(dossier_extraction, exist_ok=True)
    archive_path = os.path.join(dossier_extraction, "fond_carte_commune.7z")
    
    # Téléchargement
    response = requests.get(url_carte)
    with open(archive_path, "wb") as f:
        f.write(response.content)
    
    # Extraction - Correction de l'extraction
    with py7zr.SevenZipFile(archive_path, mode='r') as fichier:
        file_list = fichier.getnames()  # Récupère la liste des fichiers contenus dans l'archive
        fichier.extractall(dossier_extraction)
    
    # Récupération du fichier SHP - Correction pour s'assurer de trouver le bon fichier
    shp_files = [f for f in file_list if f.lower().endswith('.shp')]
    
    if not shp_files:  # Si liste vide, parcourir le dossier pour trouver les fichiers .shp
        shp_files = []
        for root, dirs, files in os.walk(dossier_extraction):
            for file in files:
                if file.lower().endswith('.shp'):
                    shp_files.append(os.path.join(root, file))
        
        if not shp_files:
            raise FileNotFoundError("Aucun fichier SHP trouvé dans l'archive extraite")
            
    shp_file_path = os.path.join(dossier_extraction, shp_files[0])
    
    # Vérifier si le chemin existe
    if not os.path.exists(shp_file_path):
        # Si le chemin complet ne fonctionne pas, essayer de trouver le fichier dans les sous-dossiers
        for root, dirs, files in os.walk(dossier_extraction):
            for file in files:
                if file.lower() == os.path.basename(shp_files[0]).lower():
                    shp_file_path = os.path.join(root, file)
                    break
    
    print(f"Utilisation du fichier SHP: {shp_file_path}")    
    
    # Chargement des données géographiques
    communes_gdf = gpd.read_file(shp_file_path)
    
    # Ajustement des codes
    communes_gdf['code'] = communes_gdf['INSEE_COM'].astype(str)
    communes_gdf.loc[communes_gdf['code'].isin(map(str, range(69381, 69390))), 'code'] = '69123'
    
    return communes_gdf

def generer_cartes_emploi(communes_gdf, paris_df, lyon_df):
    """Génération des cartes d'emploi - méthode révisée pour être compatible avec cartesParis-Lyon.py"""
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(f"{REPERTOIRE_SORTIE}/img/carte", exist_ok=True)
    
    # Préparation des données d'emploi pour Paris (assurons-nous que les colonnes existent)
    paris_cols = ['code']
    lyon_cols = ['code']
    
    for annee in PERIODES:
        col_name = f'Total_Emploi_{annee}'
        if col_name in paris_df.columns:
            paris_cols.append(col_name)
        if col_name in lyon_df.columns:
            lyon_cols.append(col_name)
    
    # Fusion des données géographiques avec les données d'emploi pour Paris et Lyon
    paris_com_gdf = communes_gdf.merge(
        paris_df[paris_cols], 
        on='code', 
        how='inner'
    )
    
    lyon_com_gdf = communes_gdf.merge(
        lyon_df[lyon_cols], 
        on='code', 
        how='inner'
    )
    
    # Définition de la colormap
    cmap = plt.cm.OrRd
    
    for annee in PERIODES:
        # PARIS
        # Normalisation des couleurs pour Paris
        norm_paris = plt.Normalize(
            vmin=paris_com_gdf[f'Total_Emploi_{annee}'].min(), 
            vmax=paris_com_gdf[f'Total_Emploi_{annee}'].max()
        )
        
        # Création de la carte pour Paris
        fig, ax = plt.subplots(figsize=(10, 10))
        paris_com_gdf.plot(
            column=f'Total_Emploi_{annee}', 
            cmap=cmap, 
            ax=ax, 
            edgecolor='black', 
            linewidth=0.05
        )
        
        plt.title(f"Nombre d'emplois par commune de l'agglomération parisienne en {annee}")
        plt.axis('off')
        
        # Barre de couleur
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_paris)
        fig.colorbar(sm, ax=ax, label="Nombre d'emplois")
        
        # Sauvegarde
        plt.savefig(
            f"{REPERTOIRE_SORTIE}/img/carte/carte_lieu_emplois_Paris_{annee}.png", 
            dpi=300, 
            bbox_inches='tight',
            pad_inches=0.1
        )
        plt.close()
        
        # LYON
        # Normalisation des couleurs pour Lyon
        norm_lyon = plt.Normalize(
            vmin=lyon_com_gdf[f'Total_Emploi_{annee}'].min(), 
            vmax=lyon_com_gdf[f'Total_Emploi_{annee}'].max()
        )
        
        # Création de la carte pour Lyon
        fig, ax = plt.subplots(figsize=(10, 10))
        lyon_com_gdf.plot(
            column=f'Total_Emploi_{annee}', 
            cmap=cmap, 
            ax=ax, 
            edgecolor='black', 
            linewidth=0.05
        )
        
        plt.title(f"Nombre d'emplois par commune de l'agglomération lyonnaise en {annee}")
        plt.axis('off')
        
        # Barre de couleur
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_lyon)
        fig.colorbar(sm, ax=ax, label="Nombre d'emplois")
        
        # Sauvegarde
        plt.savefig(
            f"{REPERTOIRE_SORTIE}/img/carte/carte_lieu_emplois_Lyon_{annee}.png", 
            dpi=300, 
            bbox_inches='tight',
            pad_inches=0.1
        )
        plt.close()
    
    return paris_com_gdf, lyon_com_gdf

def calculer_distances(communes_gdf, centre):
    """Calcul des distances par rapport à un centre"""
    def distance_centre(row):
        point = Point(row["X_CENTROID"], row["Y_CENTROID"])
        return point.distance(centre) / 1000  # km
    
    communes_gdf['distance_km'] = communes_gdf.apply(distance_centre, axis=1)
    return communes_gdf

def analyser_relation_emploi_distance(communes_gdf, ville):
    """Analyse de la relation entre emploi et distance"""
    os.makedirs(REPERTOIRE_SORTIE, exist_ok=True)
    
    for annee in PERIODES:
        # Préparation des données
        df_analyse = communes_gdf[communes_gdf['distance_km'] > 0].copy()
        
        # Filtrer les valeurs d'emploi nulles ou négatives
        df_analyse = df_analyse[df_analyse[f'Total_Emploi_{annee}'] > 0].copy()
        
        # Transformations logarithmiques
        df_analyse['log_distance'] = np.log(df_analyse['distance_km'])
        df_analyse['log_emploi'] = np.log(df_analyse[f'Total_Emploi_{annee}'].astype(float))
        
        # Vérification des valeurs NaN
        df_analyse = df_analyse.dropna(subset=['log_distance', 'log_emploi'])
        
        # Régression (seulement si nous avons assez de données)
        if len(df_analyse) > 2:
            modele = smf.ols(f"log_emploi ~ log_distance", data=df_analyse).fit()

            # Sauvegarde des résultats détaillés
            output_chemin_ols = f"{REPERTOIRE_SORTIE}/MCO_dist_emploi_{ville}_{annee}.txt"
            with open(output_chemin_ols, "w") as f:
                f.write(modele.summary().as_text())
            
            # Affichage des résultats
            print(f" Résultats pour agglomération {ville} {annee}: ")
            print(modele.summary())
            print()

            # Visualisation
            plt.figure(figsize=(10, 6))
            sns.regplot(
                x=df_analyse['log_distance'], 
                y=df_analyse['log_emploi'], 
                scatter_kws={'alpha':0.6}
            )
            plt.title(f"Relation Emploi-Distance {ville} {annee}")
            plt.xlabel("Log Distance (km)")
            plt.ylabel("Log Nombre d'Emplois")
            plt.legend([f"R² = {modele.rsquared:.2f}"])
            
            plt.savefig(
                f"{REPERTOIRE_SORTIE}/relation_emploi_{ville}_{annee}.png"
            )
            plt.close()
        else:
            print(f"AVERTISSEMENT: Pas assez de données pour l'analyse de régression pour {ville} {annee}")
            # Écrire un fichier texte expliquant le problème
            output_chemin_ols = f"{REPERTOIRE_SORTIE}/MCO_dist_emploi_{ville}_{annee}.txt"
            with open(output_chemin_ols, "w") as f:
                f.write(f"Pas assez de données valides pour l'analyse de régression pour {ville} {annee}\n")

def repartition_emplois_cumulatifs(communes_gdf, ville):
    """Analyse de la répartition cumulative des emplois"""
    os.makedirs(REPERTOIRE_SORTIE, exist_ok=True)

    for annee in PERIODES:
        # Vérifier que les données existent et sont valides
        if f'Total_Emploi_{annee}' not in communes_gdf.columns:
            print(f"AVERTISSEMENT: Pas de données d'emploi pour {ville} {annee}")
            continue
            
        # Vérifier que la colonne distance existe
        if 'distance_km' not in communes_gdf.columns:
            print(f"AVERTISSEMENT: Pas de données de distance pour {ville}")
            continue
            
        # Filtrer les valeurs manquantes ou invalides
        df_analyse = communes_gdf[~communes_gdf[f'Total_Emploi_{annee}'].isna()].copy()
        df_analyse = df_analyse[~df_analyse['distance_km'].isna()].copy()
        
        if len(df_analyse) == 0:
            print(f"AVERTISSEMENT: Aucune donnée valide pour {ville} {annee}")
            continue
            
        # Tri par distance
        df_analyse = df_analyse.sort_values('distance_km').copy()
        
        # S'assurer que nous avons un total d'emplois non nul
        total_emplois = df_analyse[f'Total_Emploi_{annee}'].sum()
        if total_emplois <= 0:
            print(f"AVERTISSEMENT: Total d'emplois nul ou négatif pour {ville} {annee}")
            continue
        
        # Calcul de la part cumulée
        df_analyse['part_emplois_cumules'] = (
            df_analyse[f'Total_Emploi_{annee}'].cumsum() / total_emplois
        )
        
        # Part dans les 10 premiers km (si des données existent)
        df_10km = df_analyse.loc[df_analyse['distance_km'] < 10]
        if len(df_10km) > 0:
            part_10km = df_10km['part_emplois_cumules'].max()
            print(f"{ville} {annee} : {part_10km:.2%} des emplois dans les 10 premiers km")
        else:
            print(f"{ville} {annee} : Pas de données dans les 10 premiers km")
        
        # Visualisation
        plt.figure(figsize=(10, 6))
        plt.plot(df_analyse['distance_km'], df_analyse['part_emplois_cumules'])
        plt.title(f"Répartition Cumulative Emplois {ville} {annee}")
        plt.xlabel("Distance (km)")
        plt.ylabel("Part Cumulée Emplois")
        
        plt.savefig(
            f"{REPERTOIRE_SORTIE}/emplois_cumules_{ville}_{annee}.png",
            dpi=300, 
            bbox_inches='tight', 
            pad_inches=0.1
        )
        plt.close()

# Exécution principale
def executer_analyse():
    # Chemins des fichiers
    chemin_emploi = f"{REPERTOIRE_ENTREE}/pop-act2554-empl-csp-cd-trav-6821_lieu-travail.xlsx"
    chemin_zones = f"{REPERTOIRE_ENTREE}/AU2010_au_01-01-2020.xlsx"
    url_carte = "https://data.geopf.fr/telechargement/download/GEOFLA/GEOFLA_2-2_COMMUNE_SHP_LAMB93_FXX_2016-06-28/GEOFLA_2-2_COMMUNE_SHP_LAMB93_FXX_2016-06-28.7z"
    
    try:
        print("Préparation des données d'emploi...")
        # Préparation des données
        donnees_emploi = preparer_donnees_emploi(chemin_emploi)
        paris_df, lyon_df = filtrer_agglomeration(donnees_emploi, chemin_zones)
        
        print("Chargement des données géographiques...")
        # Données géographiques
        communes_gdf = charger_donnees_geographiques(url_carte, f"{REPERTOIRE_ENTREE}/carte")
        
        print("Génération des cartes d'emploi...")
        # Génération des cartes (fonction modifiée)
        paris_com_gdf, lyon_com_gdf = generer_cartes_emploi(communes_gdf, paris_df, lyon_df)
        
        # Centres de référence
        centre_paris = Point(651196, 6862551)  # Coordonnées précises de Notre-Dame de Paris via Lambert-93
        centre_lyon = Point(842072, 6519805)  # Basilique Notre-Dame de Fourvière à Lyon (Lambert-93)
        
        try:
            print("Analyse pour Paris...")
            # Calcul des distances pour Paris
            paris_com_gdf = calculer_distances(paris_com_gdf, centre_paris)
            analyser_relation_emploi_distance(paris_com_gdf, "Paris")
            repartition_emplois_cumulatifs(paris_com_gdf, "Paris")
        except Exception as e:
            print(f"Erreur lors de l'analyse pour Paris: {e}")
        
        try:
            print("Analyse pour Lyon...")
            # Calcul des distances pour Lyon
            lyon_com_gdf = calculer_distances(lyon_com_gdf, centre_lyon)
            analyser_relation_emploi_distance(lyon_com_gdf, "Lyon")
            repartition_emplois_cumulatifs(lyon_com_gdf, "Lyon")
        except Exception as e:
            print(f"Erreur lors de l'analyse pour Lyon: {e}")
        
        print("Analyse terminée !")
    except Exception as e:
        print(f"Erreur lors de l'exécution de l'analyse: {e}")

# Lancement de l'analyse si exécuté comme script principal
if __name__ == "__main__":
    executer_analyse()