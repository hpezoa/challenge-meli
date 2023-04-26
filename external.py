import requests
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from utils import check_permissions, get_permissions
import db as database

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
client = database.init()
users_collection = client["users"]
data_collection = client["data"]
jwt = JWTManager(app)

# define a route to handle GET requests to fetch objects from a website
@app.route('/external/fetch-objects', methods=['GET'])
@jwt_required()
def fetch_objects():
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(user['profile'], ['update'], "external")
    # fetch objects from a website
    response = requests.get('https://62433a7fd126926d0c5d296b.mockapi.io/api/v1/usuarios')
    object_list = response.json()
    data_collection.insert_many(object_list)
    
    # return a success message
    return jsonify({'message': f"{len(object_list)} objects fetched and stored successfully"})

@app.route('/external/objects', methods=['GET'])
@jwt_required()
def list_objects():
    current_user = get_jwt_identity()
    data = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(data['profile'], ['list'], "external")
    requested = {}
    permissions = get_permissions(data['profile'])
    for access in permissions['objects']:
          requested.update({access:1})

    objects = data_collection.find({}, requested)
    # Convertir los objetos ObjectId en cadenas de texto
    objects = [object for object in objects]
    for object in objects:
        object['_id'] = str(object['_id'])

    return jsonify({'data': objects}), 200