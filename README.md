# 🏢 Urban-Economics

Problématique : **Paris et Lyon sont-elles toujours des agglomérations monocentriques ?**  
Un projet d'analyse empirique fondé sur des modèles d'économie urbaine.

## 🎯 Objectif du projet

Ce projet vise à étudier l'évolution de la répartition spatiale des emplois dans les métropoles françaises de **Paris** et **Lyon**, entre **1968 et 2021**, pour déterminer si ces villes suivent encore un modèle **monocentrique** ou tendent vers un **polycentrisme**.

L'analyse repose sur le cadre théorique du **modèle monocentrique d’Alonso (1964)**, confronté à des données réelles et des visualisations cartographiques.

## 📁 Structure du projet

```bash
Urban-Economics/
│
├── do/                  # Scripts Python pour le traitement et l'analyse
│   └── analysis.py
│
├── input/               # Fichiers Excel contenant les données INSEE
│
├── output/              # Résultats : graphiques, cartes, fichiers texte
│
├── Présentation.pdf     # Support théorique et présentation du projet
│
├── requirements.txt     # Bibliothèques nécessaires
│
└── LICENSE
```

## ⚙️ Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/jkengineer42/Urban-Economics.git
cd Urban-Economics
```

### 2. Installer les dépendances

Crée un environnement virtuel (optionnel mais recommandé) :

```bash
python -m venv env
source env/bin/activate  # sous Windows : env\Scripts\activate
```

Puis installe les bibliothèques nécessaires :

```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

Lancer le script principal :

```bash
python do/analysis.py
```

Les résultats sont générés dans le dossier `output/` sous forme de graphiques (.png) et de tableaux (.txt).

## 📊 Résultats attendus

- **Cartes** d’évolution de l’emploi à Paris et Lyon (1968, 1999, 2021)
- **Graphiques** de concentration de l’emploi
- **Régression linéaire** sur la densité d’emploi en fonction de la distance au centre
- Comparaison entre modèle monocentrique théorique et observations empiriques

## 📘 Théorie économique

Le projet s’appuie principalement sur :

- **Alonso (1964)** – Modèle monocentrique
- Notions de **coût de transport**, **loyers décroissants**, et **fonction d’enchère**
- Les limites du modèle sont discutées (polycentrisme, hétérogénéité des ménages, dynamiques temporelles)

## 👥 Auteurs

- Jérémie Konda  
- Alexandre Klobb  

## 📄 Licence

Ce projet est sous licence **BSD 2-Clause**. Voir le fichier [LICENSE](LICENSE) pour plus d’informations.
