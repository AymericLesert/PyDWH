# PyDWH

Gestion de l'entrepot de données

# Liste des packages de l'environnement de déveppoment

- pip
- build

```
$> python -m pip install --upgrade pip
$> python -m pip install build
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
