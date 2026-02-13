<<<<<<< HEAD
# ClientFlow
=======
# ClientFlow - Gestion Clients

Une application professionnelle de suivi des clients et de leurs ventes/paiements.

## Fonctionnalités

- ✅ Gestion complète des clients (ajout, consultation)
- ✅ Suivi des ventes par client avec **description des items vendus**
- ✅ **Génération automatique des numéros de référence** (format: V20260131123456789)
- ✅ Gestion des paiements avec colonne "Action" pour payer
- ✅ Export PDF professionnel avec **noms de fichiers intelligents**
- ✅ Interface moderne et intuitive avec espacement optimisé
- ✅ Calcul automatique des soldes en **Dinar Tunisien (DT)**
- ✅ Tooltips informatifs sur tous les boutons

### Configuration Régionale

L'application est configurée pour la **Tunisie** :
- **Devise** : Dinar Tunisien (DT)
- **Langue** : Français
- **Format des dates** : JJ/MM/AAAA

## Améliorations Récentes
- **Colonne Description** : Ajout d'une colonne description pour détailler les items vendus
- **Interface d'ajout de vente** : Boîte de dialogue améliorée avec champs référence, description et montant
- **Export PDF optimisé** : Liste clients sans colonne détails, espacement amélioré
- **Correction de classe manquante** : Restauration de AddClientDialog
- **Requêtes optimisées** : Jointures SQL pour de meilleures performances
- **Interface utilisateur modernisée** : Thème professionnel avec couleurs cohérentes
- **Gestion d'erreurs complète** : Messages informatifs avec validation des données
- **Compatibilité PySide6** : Corrections pour les méthodes print_ et getDouble

### Format Professionnel
- Style moderne inspiré de Windows 11
- Icônes et couleurs cohérentes
- Typographie améliorée
- Boutons stylisés selon leur fonction

## Utilisation

### Table des Ventes (Fiche Client)
- **Date** : Date de la vente
- **Référence** : Numéro de référence généré automatiquement (format: V20260131123456789)
- **Description** : Description des items vendus
- **Total DT** : Montant total de la vente en dinars tunisiens
- **Payé DT** : Montant déjà payé
- **Reste DT** : Montant restant à payer
- **Action** : Bouton "💰 Payer" pour enregistrer un paiement

### Export PDF
- **Liste clients** : `liste_clients_YYYYMMDD_HHMMSS.pdf`
- **Ventes client** : `ventes_NomClient_YYYYMMDD_HHMMSS.pdf`

### Fonctionnalités Principales

1. **Ajouter un Client** : Bouton "➕ Ajouter client" → Remplir nom, téléphone, adresse, email
2. **Voir les Détails** : Clic sur "👁️ Voir" pour un client
3. **Ajouter une Vente** : Dans la fiche client, bouton "➕ Nouvelle vente" → Référence générée automatiquement, saisir description et montant
4. **Enregistrer un Paiement** : Bouton "💰 Payer" sur les ventes impayées
5. **Exporter en PDF** : Boutons d'impression et PDF disponibles

## Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
```

2. Activer l'environnement :
```bash
# Windows
venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Lancer l'application :
```bash
python main.py
```

### Fonctionnalités Principales

1. **Ajouter un Client** : Bouton "➕ Ajouter client"
2. **Voir les Détails** : Clic sur "👁️ Voir" pour un client
3. **Ajouter une Vente** : Dans la fiche client, bouton "➕ Nouvelle vente"
4. **Enregistrer un Paiement** : Bouton "💰 Payer" sur les ventes impayées
5. **Exporter en PDF** : Boutons d'impression et PDF disponibles

## Structure de la Base de Données

- `clients` : Informations des clients
- `ventes` : Ventes enregistrées
- `paiements` : Paiements des ventes

## Technologies Utilisées

- **PySide6** : Interface graphique Qt pour Python
- **SQLite** : Base de données intégrée
- **Python 3.8+** : Langage de programmation

## Développement

L'application suit les bonnes pratiques :
- Séparation des préoccupations (UI / Logique / Données)
- Gestion d'erreurs robuste
- Code optimisé et maintenable
- Interface utilisateur intuitive
>>>>>>> e08f37c (Initial commit)
