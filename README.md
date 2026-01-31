# Dashboard de Suivi des Interventions FME

Application web complète pour le suivi des interventions des Field Maintenance Engineers (FME) sur les sites télécom.

## 🚀 Fonctionnalités

### 1. Enregistrement des Interventions
- Capture des informations du FME (nom, entreprise, téléphone)
- Enregistrement du site (T-Number, nom du site)
- État du site à l'arrivée (Down, Up, Sector Failure)
- Action à mener (liste prédéfinie + possibilité d'ajout)
- Horodatage automatique de l'arrivée

### 2. Fermeture des Interventions
- Vérification de l'état final du site
- Horodatage automatique du départ
- Suivi des sites restés down après intervention

### 3. Dashboard et Statistiques
- Vue d'ensemble en temps réel
- Interventions en cours
- Historique des interventions récentes
- Statistiques globales :
  - Nombre d'interventions en cours
  - Total des interventions
  - Sites encore down
  - Taux de résolution
- Graphiques par entreprise, état initial et action

### 4. Filtres Avancés
- Par statut (en cours / terminé)
- Par entreprise
- Sites restés down
- Par période (date début - date fin)

### 5. Reporting
- Export des données possible (extension future)
- Historique complet de toutes les interventions

## 📋 Prérequis

- Python 3.8 ou supérieur
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)

## 🔧 Installation

### 1. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Ou manuellement :
```bash
pip install Flask==3.0.0 flask-cors==4.0.0
```

### 2. Lancer l'application

```bash
python app.py
```

Le serveur démarrera automatiquement sur `http://localhost:5000`

### 3. Accéder au dashboard

Ouvrez votre navigateur et accédez à :
```
http://localhost:5000
```

## 💾 Base de Données

L'application utilise **SQLite** qui ne nécessite aucune configuration ni connexion internet.

La base de données `fme_tracker.db` est créée automatiquement au premier lancement dans le répertoire de l'application.

### Structure de la base de données

#### Table `interventions`
- `id` : Identifiant unique
- `fme_name` : Nom du FME
- `company` : Entreprise
- `phone_number` : Numéro de téléphone
- `t_number` : Identifiant du site
- `site_name` : Nom du site
- `initial_state` : État initial (down, up, sector_failure)
- `action` : Action menée
- `arrival_time` : Heure d'arrivée
- `departure_time` : Heure de départ
- `final_state` : État final
- `status` : Statut (en_cours, termine)
- `created_at` : Date de création

#### Table `custom_actions`
- `id` : Identifiant unique
- `action_name` : Nom de l'action personnalisée
- `created_at` : Date de création

## 📱 Guide d'Utilisation

### Enregistrer une nouvelle intervention

1. Cliquez sur **"Nouvelle"** dans le menu latéral
2. Remplissez tous les champs requis :
   - Nom du FME
   - Entreprise
   - Numéro de téléphone
   - T-Number du site
   - Nom du site
   - État initial du site
   - Action à mener
3. Cliquez sur **"Enregistrer l'Intervention"**

💡 L'heure d'arrivée est automatiquement enregistrée

### Fermer une intervention

1. Dans le **Dashboard** ou la vue **Interventions**, repérez l'intervention en cours
2. Cliquez sur le bouton **"Fermer l'intervention"**
3. Sélectionnez l'état final du site (Down, Up, Sector Failure)
4. Cliquez sur **"Fermer l'Intervention"**

💡 L'heure de départ est automatiquement enregistrée

### Ajouter une action personnalisée

1. Dans le formulaire de nouvelle intervention
2. Cliquez sur le bouton **"+ Ajouter"** à côté du champ "Action"
3. Entrez le nom de la nouvelle action
4. Cliquez sur **"Ajouter"**

### Filtrer les interventions

1. Allez dans la vue **"Interventions"**
2. Utilisez les filtres disponibles :
   - Statut (En cours / Terminé)
   - Entreprise
   - Sites restés DOWN (case à cocher)
   - Date de début
   - Date de fin
3. Cliquez sur **"Filtrer"**
4. Pour réinitialiser : **"Réinitialiser"**

### Consulter les statistiques

1. Cliquez sur **"Statistiques"** dans le menu
2. Visualisez les graphiques :
   - Interventions par entreprise
   - Interventions par état initial
   - Top 10 des actions

## 🎨 Interface

L'interface est conçue pour être :
- **Moderne et professionnelle** : Design sombre avec des accents orangés
- **Intuitive** : Navigation simple et claire
- **Responsive** : S'adapte aux différentes tailles d'écran
- **Temps réel** : Actualisation automatique toutes les 30 secondes

### Navigation

- **📊 Dashboard** : Vue d'ensemble et interventions en cours
- **📋 Interventions** : Historique complet avec filtres
- **➕ Nouvelle** : Enregistrer une nouvelle intervention
- **📈 Statistiques** : Analyses et graphiques

## 🔒 Sécurité et Données

- ✅ Base de données locale (SQLite)
- ✅ Aucune connexion internet requise
- ✅ Données stockées en local
- ✅ Pas de dépendance externe

## 🛠️ Support et Personnalisation

### Modifier les actions prédéfinies

Éditez le fichier `app.py`, section `PREDEFINED_ACTIONS` :

```python
PREDEFINED_ACTIONS = [
    "Remplacement d'équipement",
    "Maintenance préventive",
    # Ajoutez vos actions ici
]
```

### Modifier le port

Par défaut, l'application tourne sur le port 5000. Pour changer :

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changez 8080 par votre port
```

### Sauvegarder la base de données

Copiez simplement le fichier `fme_tracker.db` vers un emplacement sûr.

## 📊 Capacité

L'application peut gérer confortablement :
- ✅ 15-20 interventions par jour
- ✅ Des milliers d'interventions dans l'historique
- ✅ Plusieurs utilisateurs simultanés (superviseurs)

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifiez que Python est installé
python --version

# Vérifiez les dépendances
pip install -r requirements.txt
```

### La page ne se charge pas
- Vérifiez que le serveur est démarré
- Accédez à `http://localhost:5000` (pas 127.0.0.1)
- Videz le cache du navigateur

### Les données ne s'affichent pas
- Vérifiez la console JavaScript (F12 dans le navigateur)
- Redémarrez le serveur
- Actualisez la page (F5)

## 📝 Notes

- L'application est conçue pour fonctionner **sans internet**
- La base de données SQLite est **légère et portable**
- Les **actions personnalisées** sont sauvegardées définitivement
- Le **taux de résolution** est calculé automatiquement

## 🚀 Évolutions Futures Possibles

- Export Excel/PDF des rapports
- Notifications par email/SMS
- Application mobile native
- Intégration avec d'autres systèmes
- Authentification multi-utilisateurs
- Tableau de bord temps réel avec WebSocket

---

**Développé pour le suivi efficace des interventions FME sur les sites télécom** 📡
