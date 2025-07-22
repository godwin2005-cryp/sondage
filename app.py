from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

# Fichier pour stocker les sondages
SURVEYS_FILE = 'surveys.json'

def load_surveys():
    """Charge les sondages depuis le fichier JSON"""
    if os.path.exists(SURVEYS_FILE):
        try:
            with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_surveys(surveys):
    """Sauvegarde les sondages dans le fichier JSON"""
    with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(surveys, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Page d'accueil avec le formulaire de sondage"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Page de connexion administrateur"""
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Traitement de la connexion administrateur"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Authentification simple (à améliorer en production)
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Identifiants incorrects'})

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion administrateur"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def dashboard():
    """Tableau de bord administrateur"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    surveys = load_surveys()
    return render_template('dashboard.html', surveys=surveys)

@app.route('/api/submit_survey', methods=['POST'])
def submit_survey():
    """Soumission d'un nouveau sondage"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['satisfaction', 'category', 'comment']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Le champ {field} est requis'})
        
        # Création du sondage
        survey = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'satisfaction': int(data['satisfaction']),
            'category': data['category'],
            'comment': data['comment'],
            'would_recommend': data.get('would_recommend', False),
            'improvements': data.get('improvements', [])
        }
        
        # Sauvegarde
        surveys = load_surveys()
        surveys.append(survey)
        save_surveys(surveys)
        
        return jsonify({'success': True, 'message': 'Avis enregistré avec succès'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erreur lors de l\'enregistrement'})

@app.route('/api/surveys')
def get_surveys():
    """Récupération des sondages pour l'admin"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Non autorisé'}), 401
    
    surveys = load_surveys()
    return jsonify(surveys)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)