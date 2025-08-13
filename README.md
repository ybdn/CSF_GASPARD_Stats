# Application de Traitement de Données

Une application Python avec interface graphique pour importer, traiter des données et générer des statistiques en utilisant un annuaire de référence.

## Fonctionnalités

- Interface graphique intuitive avec PyQt5
- Importation de données depuis différents formats (CSV, Excel)
- **Création d'un annuaire interne par fusion de deux fichiers sources :**
  - Sélection des fichiers et des colonnes clés.
  - **Possibilité de supprimer des colonnes spécifiques de chaque fichier source avant la fusion.**
  - Formatage automatique des clés au format `GN` + 8 chiffres.
  - Combinaison automatique des lignes ayant la même clé après fusion.
- **Traitement des données importées en utilisant l'annuaire interne :**
  - Sélection de la colonne clé dans les données importées.
  - Formatage automatique de cette clé (`GN` + 8 chiffres).
  - Fusion efficace (`pd.merge`) avec l'annuaire.
- Génération et visualisation de statistiques combinées (Globales et spécifiques 'SM') sur les données enrichies, avec formatage des codes département (ex: '01').
- Exportation des données traitées et des statistiques combinées.

## Prérequis

- Python 3.6+
- Bibliothèques Python requises (voir `requirements.txt`)

## Installation

1. Clonez ce dépôt :

```bash
git clone https://github.com/votreusername/app-traitement-donnees.git
cd app-traitement-donnees
```

2. Créez un environnement virtuel (recommandé) :

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\\Scripts\\activate
```

3. Installez les dépendances :

```bash
pip3 install -r requirements.txt
```

## Utilisation

1. Lancez l'application :

```bash
python3 app/main.py
```

2. Utilisation de l'interface :
   - **Créer/Mettre à jour l'annuaire interne (Onglet "Fusion d'Annuaires") :**
     - Utilisez les boutons "Parcourir..." pour sélectionner les deux fichiers CSV sources (ex: unités, matériels).
     - Sélectionnez la colonne clé pour chaque fichier dans les menus déroulants.
     - Dans les listes correspondantes, cochez les colonnes que vous souhaitez **supprimer** de chaque fichier source avant la fusion.
     - Choisissez le type de fusion (ex: 'outer' pour tout garder) et le nom du fichier annuaire cible.
     - Cliquez sur "Fusionner les fichiers". L'application formatera les clés, supprimera les colonnes sélectionnées, fusionnera les fichiers et sauvegardera l'annuaire interne.
   - **Importer et traiter les données (Onglet "Import de Données") :**
     - Importez vos données principales (ex: signalisations) de deux manières :
       - Via le menu "Fichier > Importer des données..." (pour fichiers CSV ou Excel).
       - Ou, pour une extraction spécifique, utilisez le bouton "Importer Extraction ANFSI" directement dans cet onglet (pour fichiers CSV uniquement).
     - Dans l'onglet "Import de Données", configurez les options de traitement avant la fusion :
       - **Colonne Clé (fusion) :** Sélectionnez la colonne de vos données contenant la clé à associer à l'annuaire (ex: `code_service`). Cette colonne sera formatée (`GN` + 8 chiffres).
       - **Colonne Type (optionnel) :** Sélectionnez la colonne contenant le type de signalisation (ex: 'SM'). Si une colonne est sélectionnée ici, la fusion sera conditionnelle :
         - Pour les lignes où cette colonne vaut 'SM' (insensible à la casse), seules les colonnes `abrege_unite` et `departement` de l'annuaire seront ajoutées.
         - Pour les autres lignes, toutes les colonnes de l'annuaire seront ajoutées.
       - **Colonnes à supprimer (avant fusion) :** Dans la liste de droite, cochez les colonnes de vos données importées que vous souhaitez supprimer **avant** d'effectuer la fusion avec l'annuaire. (Note: Les colonnes sélectionnées comme Clé ou Type ne peuvent pas être supprimées et seront automatiquement décochées si sélectionnées).
     - Cliquez sur le bouton **"Traiter et Exporter"**. L'application effectuera les actions suivantes :
       1. Suppression des colonnes sélectionnées.
       2. Formatage de la colonne Clé.
       3. Fusion (conditionnelle si la colonne Type est spécifiée) avec l'annuaire interne.
       4. Exportation automatique du résultat complet dans un fichier `exports/STATS_GASPARD_[MOIS]-[ANNÉE].csv`.
     - Un message confirmera le succès de l'exportation ou indiquera une erreur.
     - Basculez sur l'onglet **"Statistiques Combinées"** pour visualiser les statistiques générées (Globales et SM) à partir des données fusionnées. Les statistiques sont présentées dans un **tableau unique** avec une colonne **"Type Statistique"** indiquant l'origine ('Globale' ou 'SM'). Les codes département sont formatés sur deux chiffres (ex: '01').
     - Exportez ce tableau combiné via le bouton **"Exporter Tableau Combiné"** (formats CSV ou Excel).

## Structure du projet

```
app/
├── main.py                 # Point d'entrée principal
├── gui/                    # Interface utilisateur
│   ├── main_window.py      # Fenêtre principale
│   ├── import_view.py      # Vue d'importation
│   ├── stats_view.py       # Vue des statistiques
│   └── directory_merge_view.py # Vue de gestion de l'annuaire
├── core/                   # Logique métier
│   └── data_processor.py   # Traitement des données
├── utils/                  # Utilitaires
│   ├── file_handlers.py    # Gestion des fichiers
│   └── directory_manager.py # Gestion de l'annuaire
└── resources/              # Ressources
    └── directory/          # Fichiers d'annuaire
exports/                    # Répertoire pour les fichiers exportés
```

## Gestion de l'annuaire

L'annuaire de référence utilisé par l'application est généré dynamiquement en fusionnant deux fichiers sources (par exemple, un fichier d'unités et un fichier de matériels) via l'onglet "Fusion d'Annuaires".

Lors de la configuration et fusion des annuaires sources :

1.  L'utilisateur sélectionne les deux fichiers CSV sources.
2.  L'utilisateur choisit la colonne clé dans chaque fichier qui servira à la fusion.
3.  L'utilisateur peut **cocher les colonnes à supprimer** de chaque fichier source avant la fusion.
4.  L'application **formate automatiquement** les valeurs des colonnes clés retenues au format standard `GN` + 8 chiffres (ex: `GN12345678`).
5.  L'application supprime les colonnes sélectionnées pour suppression.
6.  Les deux fichiers préparés sont ensuite fusionnés (type de jointure choisi par l'utilisateur, 'outer' par défaut) en utilisant les clés formatées.
7.  Les lignes ayant la même clé `GN` dans le résultat sont combinées pour éviter les doublons.
8.  Le résultat est stocké comme l'annuaire interne de l'application (par défaut `app/resources/directory/directory.csv`, mais le nom peut être changé dans l'interface).

Cet annuaire interne (avec sa colonne clé `key` formatée) est ensuite utilisé pour enrichir les données principales importées par l'utilisateur (ex: les signalisations) dans l'onglet "Import de Données". La colonne clé sélectionnée par l'utilisateur dans ces données importées est également formatée automatiquement au format `GN` + 8 chiffres avant la jointure (`left merge`).
