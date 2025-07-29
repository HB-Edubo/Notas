from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import uuid

# Inicializa Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_key', methods=['POST'])
def generate_key():
    data = request.json
    name = data.get('name')
    gmail = data.get('gmail')
    phone = data.get('phone')
    key = str(uuid.uuid4())[:8]  # Clave corta
    db.collection('keys').document(key).set({
        'name': name,
        'gmail': gmail,
        'phone': phone,
        'uses': 10,  # usos por defecto
        'activated': False
    })
    return jsonify({'success': True, 'key': key})

@app.route('/get_keys')
def get_keys():
    docs = db.collection('keys').stream()
    keys = []
    for doc in docs:
        data = doc.to_dict()
        keys.append({
            'key': doc.id,
            'name': data.get('name'),
            'gmail': data.get('gmail'),
            'phone': data.get('phone'),
            'uses': data.get('uses'),
            'activated': data.get('activated')
        })
    return jsonify(keys)

@app.route('/update_uses', methods=['POST'])
def update_uses():
    data = request.json
    key = data.get('key')
    new_uses = data.get('uses')
    if new_uses < 0:
        new_uses = 0
    db.collection('keys').document(key).update({'uses': new_uses})
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
