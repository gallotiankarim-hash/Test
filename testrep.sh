#!/bin/bash

# Nom du répertoire racine du projet
PROJECT_ROOT="rtcef"

# --- 1. Création et navigation dans le répertoire racine ---
echo "Création du répertoire racine : $PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

# --- 2. Création des répertoires principaux et des sous-répertoires ---
echo "Création de la structure des dossiers..."

# Répertoires de premier niveau
mkdir app config core capture analysis reports ui utils

# Sous-répertoires spécifiques
mkdir capture/adapters
mkdir reports/templates

# --- 3. Création des fichiers de configuration et de base ---
echo "Création des fichiers de base..."

# Fichiers racine
touch app.py
touch requirements.txt

# Fichiers de configuration
touch config/modes.yaml
touch config/settings.yaml

# --- 4. Création des fichiers du 'core' ---
echo "Création des fichiers 'core'..."
touch core/session.py
touch core/flow.py
touch core/exposure.py
touch core/peer.py
touch core/scoring.py
touch core/events.py

# --- 5. Création des fichiers de 'capture' ---
echo "Création des fichiers 'capture'..."
touch capture/interface.py
touch capture/mock.py
touch capture/adapters/pcap_adapter.py
touch capture/adapters/webrtc_adapter.py
touch capture/adapters/voip_adapter.py

# --- 6. Création des fichiers d''analysis' ---
echo "Création des fichiers 'analysis'..."
touch analysis/ice.py
touch analysis/rtp.py
touch analysis/stun.py
touch analysis/timing.py

# --- 7. Création des fichiers de 'reports' ---
echo "Création des fichiers 'reports'..."
touch reports/generator.py
# Fichiers de templates (le dossier est déjà créé)

# --- 8. Création des fichiers d''ui' ---
echo "Création des fichiers 'ui'..."
touch ui/dashboard.py
touch ui/timeline.py
touch ui/findings.py

# --- 9. Création des fichiers d''utils' ---
echo "Création des fichiers 'utils'..."
touch utils/network.py

# --- 10. Confirmation ---
echo "🎉 Structure de projet '$PROJECT_ROOT' créée avec succès !"
echo "Vous êtes maintenant dans : $(pwd)"
