from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import io
import csv

app = Flask(__name__)
CORS(app)

DATABASE = 'fme_tracker.db'

def get_db():
    """Connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialisation de la base de données"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Table des entreprises
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des FME
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fme_name TEXT NOT NULL,
            company_id INTEGER NOT NULL,
            phone_number TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fme_name, company_id),
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Table des sites
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            t_number TEXT UNIQUE NOT NULL,
            site_name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des interventions avec système de tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            fme_id INTEGER NOT NULL,
            t_number TEXT NOT NULL,
            site_name TEXT NOT NULL,
            initial_state TEXT NOT NULL,
            action TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            departure_time TEXT,
            final_state TEXT,
            comment TEXT,
            status TEXT DEFAULT 'en_cours',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fme_id) REFERENCES fme (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Page principale"""
    # Lire et servir le fichier HTML React directement
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Récupérer toutes les entreprises"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, company_name FROM companies ORDER BY company_name')
    companies = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(companies)

@app.route('/api/companies', methods=['POST'])
def add_company():
    """Ajouter une nouvelle entreprise"""
    data = request.json
    company_name = data.get('company_name', '').strip()
    
    if not company_name:
        return jsonify({'error': 'Le nom de l\'entreprise est requis'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO companies (company_name) VALUES (?)', (company_name,))
        company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': company_id, 'company_name': company_name})
    except sqlite3.IntegrityError:
        # Entreprise existe déjà
        cursor.execute('SELECT id, company_name FROM companies WHERE company_name = ?', (company_name,))
        existing = cursor.fetchone()
        conn.close()
        return jsonify({'success': True, 'id': existing['id'], 'company_name': existing['company_name']})

@app.route('/api/fme', methods=['GET'])
def get_fme_list():
    """Récupérer tous les FME"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.id, f.fme_name, c.company_name, f.phone_number 
        FROM fme f
        LEFT JOIN companies c ON f.company_id = c.id
        ORDER BY f.fme_name
    ''')
    fme_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(fme_list)

@app.route('/api/fme/search', methods=['GET'])
def search_fme():
    """Rechercher un FME par nom"""
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.id, f.fme_name, c.company_name, f.phone_number 
        FROM fme f
        LEFT JOIN companies c ON f.company_id = c.id
        WHERE f.fme_name LIKE ? OR c.company_name LIKE ?
        ORDER BY f.fme_name
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(results)

@app.route('/api/fme', methods=['POST'])
def add_fme():
    """Ajouter un nouveau FME"""
    data = request.json
    fme_name = data.get('fme_name', '').strip()
    company_name = data.get('company_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    
    if not fme_name or not company_name or not phone_number:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Vérifier/créer l'entreprise
    cursor.execute('SELECT id FROM companies WHERE company_name = ?', (company_name,))
    company = cursor.fetchone()
    
    if company:
        company_id = company['id']
    else:
        cursor.execute('INSERT INTO companies (company_name) VALUES (?)', (company_name,))
        company_id = cursor.lastrowid
    
    try:
        cursor.execute('''
            INSERT INTO fme (fme_name, company_id, phone_number) 
            VALUES (?, ?, ?)
        ''', (fme_name, company_id, phone_number))
        fme_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': fme_id, 'fme_name': fme_name, 'company_name': company_name, 'phone_number': phone_number})
    except sqlite3.IntegrityError:
        # FME existe déjà, le récupérer
        cursor.execute('''
            SELECT f.id, f.fme_name, c.company_name, f.phone_number 
            FROM fme f
            LEFT JOIN companies c ON f.company_id = c.id
            WHERE f.fme_name = ? AND f.company_id = ?
        ''', (fme_name, company_id))
        existing_fme = cursor.fetchone()
        conn.close()
        return jsonify({'success': True, 'id': existing_fme['id'], 'fme_name': existing_fme['fme_name'], 'company_name': existing_fme['company_name'], 'phone_number': existing_fme['phone_number']})

@app.route('/api/sites', methods=['GET'])
def get_sites():
    """Récupérer tous les sites"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT t_number, site_name FROM sites ORDER BY t_number')
    sites = [{'t_number': row['t_number'], 'site_name': row['site_name']} for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(sites)

@app.route('/api/sites/<t_number>', methods=['GET'])
def get_site_by_tnumber(t_number):
    """Récupérer un site par son T-Number"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT t_number, site_name FROM sites WHERE t_number = ?', (t_number,))
    site = cursor.fetchone()
    
    conn.close()
    
    if site:
        return jsonify({'t_number': site['t_number'], 'site_name': site['site_name']})
    else:
        return jsonify({'error': 'Site non trouvé'}), 404

@app.route('/api/interventions/search', methods=['GET'])
def search_interventions():
    """Rechercher des interventions par T-Number ou ticket"""
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            i.id, i.ticket_number, i.t_number, i.site_name, i.initial_state, i.action,
            i.arrival_time, i.departure_time, i.final_state, i.comment, i.status, i.created_at,
            f.fme_name, c.company_name, f.phone_number
        FROM interventions i
        LEFT JOIN fme f ON i.fme_id = f.id
        LEFT JOIN companies c ON f.company_id = c.id
        WHERE i.t_number LIKE ? OR i.ticket_number LIKE ? OR i.site_name LIKE ?
        ORDER BY i.created_at DESC
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    interventions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(interventions)

@app.route('/api/sites', methods=['POST'])
def add_site():
    """Ajouter un nouveau site"""
    data = request.json
    t_number = data.get('t_number', '').strip()
    site_name = data.get('site_name', '').strip()
    
    if not t_number or not site_name:
        return jsonify({'error': 'T-Number et nom du site requis'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO sites (t_number, site_name) VALUES (?, ?)', (t_number, site_name))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 't_number': t_number, 'site_name': site_name})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Ce T-Number existe déjà'}), 400

@app.route('/api/suggestions/actions', methods=['GET'])
def get_action_suggestions():
    """Récupérer les suggestions d'actions depuis les interventions passées"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT action 
        FROM interventions 
        WHERE action IS NOT NULL AND action != ''
        ORDER BY action
    ''')
    actions = [row['action'] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(actions)

@app.route('/api/interventions', methods=['GET'])
def get_interventions():
    """Récupérer toutes les interventions avec filtres"""
    status = request.args.get('status', '')
    company = request.args.get('company', '')
    site_down = request.args.get('site_down', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            i.id, i.ticket_number, i.t_number, i.site_name, i.initial_state, i.action,
            i.arrival_time, i.departure_time, i.final_state, i.comment, i.status, i.created_at,
            f.fme_name, c.company_name, f.phone_number
        FROM interventions i
        LEFT JOIN fme f ON i.fme_id = f.id
        LEFT JOIN companies c ON f.company_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND i.status = ?'
        params.append(status)
    
    if company:
        query += ' AND c.company_name = ?'
        params.append(company)
    
    if site_down == 'true':
        query += ' AND i.final_state = "down"'
    
    if date_from:
        query += ' AND DATE(i.arrival_time) >= DATE(?)'
        params.append(date_from)
    
    if date_to:
        query += ' AND DATE(i.arrival_time) <= DATE(?)'
        params.append(date_to)
    
    query += ' ORDER BY i.created_at DESC'
    
    cursor.execute(query, params)
    interventions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(interventions)

@app.route('/api/interventions', methods=['POST'])
def create_intervention():
    """Créer une nouvelle intervention (FME arrive sur site)"""
    data = request.json
    
    required_fields = ['fme_name', 'company_name', 'phone_number', 't_number', 'site_name', 'initial_state', 'action']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Vérifier/créer l'entreprise
    cursor.execute('SELECT id FROM companies WHERE company_name = ?', (data['company_name'],))
    company = cursor.fetchone()
    
    if company:
        company_id = company['id']
    else:
        cursor.execute('INSERT INTO companies (company_name) VALUES (?)', (data['company_name'],))
        company_id = cursor.lastrowid
    
    # Vérifier si le FME existe, sinon l'ajouter
    cursor.execute('SELECT id FROM fme WHERE fme_name = ? AND company_id = ?', 
                   (data['fme_name'], company_id))
    fme = cursor.fetchone()
    
    if fme:
        fme_id = fme['id']
        # Mettre à jour le numéro de téléphone si différent
        cursor.execute('UPDATE fme SET phone_number = ? WHERE id = ?', 
                      (data['phone_number'], fme_id))
    else:
        cursor.execute('''
            INSERT INTO fme (fme_name, company_id, phone_number) 
            VALUES (?, ?, ?)
        ''', (data['fme_name'], company_id, data['phone_number']))
        fme_id = cursor.lastrowid
    
    # Vérifier si le site existe, sinon l'ajouter
    cursor.execute('SELECT id FROM sites WHERE t_number = ?', (data['t_number'],))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO sites (t_number, site_name) VALUES (?, ?)', 
                      (data['t_number'], data['site_name']))
    
    # Générer le numéro de ticket (format: TKT-YYYYMMDD-XXXX)
    today = datetime.now().strftime('%Y%m%d')
    cursor.execute('SELECT COUNT(*) as count FROM interventions WHERE DATE(created_at) = DATE("now")')
    count_today = cursor.fetchone()['count']
    ticket_number = f'TKT-{today}-{str(count_today + 1).zfill(4)}'
    
    arrival_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO interventions 
        (ticket_number, fme_id, t_number, site_name, initial_state, action, arrival_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'en_cours')
    ''', (
        ticket_number,
        fme_id,
        data['t_number'],
        data['site_name'],
        data['initial_state'],
        data['action'],
        arrival_time
    ))
    
    intervention_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'id': intervention_id, 
        'ticket_number': ticket_number,
        'arrival_time': arrival_time
    })

@app.route('/api/interventions/<int:intervention_id>/close', methods=['PUT'])
def close_intervention(intervention_id):
    """Fermer une intervention (FME quitte le site)"""
    data = request.json
    final_state = data.get('final_state')
    comment = data.get('comment', '')  # Commentaire facultatif
    
    if not final_state:
        return jsonify({'error': 'L\'état final est requis'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    departure_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        UPDATE interventions 
        SET final_state = ?, departure_time = ?, comment = ?, status = 'termine'
        WHERE id = ?
    ''', (final_state, departure_time, comment, intervention_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'departure_time': departure_time})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Récupérer les statistiques"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Interventions en cours
    cursor.execute('SELECT COUNT(*) as count FROM interventions WHERE status = "en_cours"')
    ongoing = cursor.fetchone()['count']
    
    # Total des interventions
    cursor.execute('SELECT COUNT(*) as count FROM interventions')
    total = cursor.fetchone()['count']
    
    # Sites encore down après intervention
    cursor.execute('SELECT COUNT(*) as count FROM interventions WHERE status = "termine" AND final_state = "down"')
    still_down = cursor.fetchone()['count']
    
    # Interventions par entreprise
    cursor.execute('''
        SELECT c.company_name, COUNT(*) as count 
        FROM interventions i
        LEFT JOIN fme f ON i.fme_id = f.id
        LEFT JOIN companies c ON f.company_id = c.id
        GROUP BY c.company_name 
        ORDER BY count DESC
    ''')
    by_company = [dict(row) for row in cursor.fetchall()]
    
    # Interventions par état initial
    cursor.execute('''
        SELECT initial_state, COUNT(*) as count 
        FROM interventions 
        GROUP BY initial_state
    ''')
    by_initial_state = [dict(row) for row in cursor.fetchall()]
    
    # Interventions par action
    cursor.execute('''
        SELECT action, COUNT(*) as count 
        FROM interventions 
        GROUP BY action 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    by_action = [dict(row) for row in cursor.fetchall()]
    
    # Taux de résolution (sites qui passent de down à up)
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM interventions 
        WHERE status = "termine" AND initial_state = "down" AND final_state = "up"
    ''')
    resolved = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM interventions 
        WHERE status = "termine" AND initial_state = "down"
    ''')
    total_down = cursor.fetchone()['count']
    
    resolution_rate = (resolved / total_down * 100) if total_down > 0 else 0
    
    # Liste des entreprises
    cursor.execute('SELECT company_name FROM companies ORDER BY company_name')
    companies = [row['company_name'] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'ongoing': ongoing,
        'total': total,
        'still_down': still_down,
        'by_company': by_company,
        'by_initial_state': by_initial_state,
        'by_action': by_action,
        'resolution_rate': round(resolution_rate, 1),
        'companies': companies
    })

@app.route('/api/interventions/<int:intervention_id>', methods=['DELETE'])
def delete_intervention(intervention_id):
    """Supprimer une intervention"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM interventions WHERE id = ?', (intervention_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Exporter les interventions en Excel (CSV)"""
    status = request.args.get('status', '')
    company = request.args.get('company', '')
    site_down = request.args.get('site_down', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            i.id, i.ticket_number, f.fme_name, c.company_name, f.phone_number,
            i.t_number, i.site_name, i.initial_state, i.action,
            i.arrival_time, i.departure_time, i.final_state, i.comment, i.status, i.created_at
        FROM interventions i
        LEFT JOIN fme f ON i.fme_id = f.id
        LEFT JOIN companies c ON f.company_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND i.status = ?'
        params.append(status)
    
    if company:
        query += ' AND c.company_name = ?'
        params.append(company)
    
    if site_down == 'true':
        query += ' AND i.final_state = "down"'
    
    if date_from:
        query += ' AND DATE(i.arrival_time) >= DATE(?)'
        params.append(date_from)
    
    if date_to:
        query += ' AND DATE(i.arrival_time) <= DATE(?)'
        params.append(date_to)
    
    query += ' ORDER BY i.created_at DESC'
    
    cursor.execute(query, params)
    interventions = cursor.fetchall()
    conn.close()
    
    # Créer le CSV en mémoire
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow([
        'ID', 'Ticket', 'FME', 'Entreprise', 'Téléphone', 'T-Number', 'Site', 
        'État Initial', 'Action', 'Arrivée', 'Départ', 'État Final', 
        'Commentaire', 'Statut', 'Date Création'
    ])
    
    # Données
    for intervention in interventions:
        writer.writerow([
            intervention['id'],
            intervention['ticket_number'],
            intervention['fme_name'],
            intervention['company_name'],
            intervention['phone_number'],
            intervention['t_number'],
            intervention['site_name'],
            intervention['initial_state'],
            intervention['action'],
            intervention['arrival_time'],
            intervention['departure_time'] or '',
            intervention['final_state'] or '',
            intervention['comment'] or '',
            intervention['status'],
            intervention['created_at']
        ])
    
    # Préparer le fichier pour téléchargement
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),  # utf-8-sig pour Excel
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'interventions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    init_db()
    print("🚀 Serveur démarré sur http://localhost:5000")
    print("📊 Dashboard accessible dans votre navigateur")
    app.run(debug=True, host='0.0.0.0', port=5000)
