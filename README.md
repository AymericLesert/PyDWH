# PyDWH

Gestion de l'entrepot de données

# Liste des packages de l'environnement de déveppoment

- pip
- build

```
$> python -m pip install --upgrade pip
$> python -m pip install build
```

Pour développer :

```
$> dwh/Scripts/Activate
$> [System.Environment]::SetEnvironmentVariable("PYTHONPATH", "src\")
$> python ./src/scripts/dwh_rules.py --config ../PyDWHConfig/config.yml
```

Pour packager :

```
$> python -m build
```

# Liste des packages de l'environnement de production

- dotenv
- cryptography
- pyyaml

Pour déployer :

```
$> python -m venv dwh
$> dwh/Scripts/Activate
$> python -m pip install dist/pydwh-0.0.0.0-py3-none-any.whl
```

Lancement :

```
$> dwh/Scripts/Activate
$> dwh-key-new
```

# Cas d'usage

Cette section décrit les différents cas d'usage possibles avec PyDWH.

## Cas 1 : Analyse de la qualité des données

1. Lire le schéma d'une base de données
2. Identifier les tables à analyser
3. Analyser les valeurs présentes dans les colonnes sans application de règles (clés, formats, plages, etc.)
4. Générer un rapport d'analyse technique (détaillé et résumé)
5. Envoyer le rapport résumé par email (optionnel)

## Cas 2 : Application des règles de qualité des données

1. Lire le schéma d'une base de données
2. Identifier les tables à analyser
3. Analyser les valeurs présentes dans les colonnes
4. Appliquer les règles de qualité des données (plus ou moins complexe) - Basée sur l'application d'un arbre de décision
5. Générer un rapport d'analyse permettant d'identifier les données ne respectant pas l'arbre de décision (détaillé et résumé)
6. Envoyer le rapport résumé par email (optionnel)

## Cas 3 : Création d'un fichier CSV ou EXCEL pour des rapports automatiques

1. Lire une table ou une requête SQL
2. Appliquer des règles de transformation sur les données
3. Générer un fichier CSV ou EXCEL
4. Envoyer le fichier par email

## Cas 4 : Chargement de données dans un entrepôt de données

1. Lire le schéma d'une base de données
2. Identifier les tables à analyser
3. Analyser les valeurs présentes dans les tables
4. Appliquer les règles de qualité des données (plus ou moins complexe) - Basée sur l'application d'un arbre de décision
5. Appliquer des règles de transformation sur les données
6. Charger les données dans un entrepôt de données en tenant compte des variations
7. Générer un rapport d'analyse technique (détaillé et résumé)
8. Générer un rapport d'analyse permettant d'identifier les données ne respectant pas l'arbre de décision (détaillé et résumé)
9. Générer un rapport de chargement (détaillé et résumé)
10. Envoyer les rapports résumés par email (optionnel)

## Cas 5 : Automatisation des processus de gestion de l'entrepôt de données

1. Prévoir des opérations de maintenance (ex : nettoyage des données, archivage, etc.)
2. Suppression de données historiques sans perte d'informations
3. Suppression de colonnes inutiles
4. Générer un rapport des opérations effectuées (détaillé et résumé)
5. Envoyer le rapport résumé par email (optionnel)

## Cas 6 : Alimentation automatique de l'entrepot de données

1. Ecouter la présence de fichiers CSV ou EXCEL dans un répertoire donné
2. Lire les fichiers présents
3. Appliquer des règles de qualité des données (plus ou moins complexe) - Basée sur l'application d'un arbre de décision
4. Appliquer des règles de transformation sur les données
5. Charger les données dans un entrepôt de données en tenant compte des variations
6. Générer un rapport des opérations effectuées (détaillé et résumé)
7. Envoyer le rapport résumé par email (optionnel)

## Cas 7 : Synchronisation des utilisateurs entre l'AD Azure et une application tierce

1. Lire les utilisateurs et leurs groupes depuis l'AD Azure
2. Lire les utilisateurs et leurs groupes dans une application tierce (comme Yooz, OpenProject, ...)
3. Comparer les utilisateurs et leurs groupes entre les deux systèmes
4. Mettre à jour les utilisateurs et leurs groupes dans l'application tierce en fonction des données de l'AD Azure
5. Générer un rapport des opérations effectuées (détaillé et résumé)
6. Envoyer le rapport résumé par email (optionnel)

## Cas 8 : Historisation des mouvements des utilisateurs dans AD Azure

1. Lire les utilisateurs et leurs groupes depuis l'AD Azure
2. Comparer les utilisateurs et leurs groupes par rapport aux données présentes dans l'entrepôt de données
3. Charger les écarts dans l'entrepôt de données
4. Générer un rapport des opérations effectuées (détaillé et résumé)
5. Envoyer le rapport résumé par email (optionnel)
