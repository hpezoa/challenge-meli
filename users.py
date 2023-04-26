from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from bson.objectid import ObjectId
from utils import check_permissions
import bcrypt
import db as database

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
client = database.init()
users_collection = client["users"]
jwt = JWTManager(app)


# Endpoint para crear un nuevo usuario
@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(user['profile'], ['create'], "users")

    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    profile = data.get('profile', None)

    if not username:
        return jsonify({'message': 'Missing username parameter'}), 400
    if not password:
        return jsonify({'message': 'Missing password parameter'}), 400
    if not profile:
        return jsonify({'message': 'Missing profile parameter'}), 400

    try:
        profile = ObjectId(profile)
    except:
        return jsonify({'error': 'Invalid profile ID format'}), 400
    
    # Encriptar la contraseña del usuario
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_data = {'username': username, 'password': hashed_password, 'profile': profile}
    result = users_collection.insert_one(user_data)
    return jsonify({'message': 'User created successfully', 'id': str(result.inserted_id)}), 201

@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    data = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(data['profile'], ['list'], "users")

    users = users_collection.find({}, {'password': 0})
    # Convertir los objetos ObjectId en cadenas de texto
    users = [user for user in users]
    for user in users:
        user['_id'] = str(user['_id'])
        user['profile'] = str(user['profile'])

    return jsonify({'users': users}), 200

@app.route('/users/<string:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(user['profile'], ['get'], "users")

    try:
        user_id = ObjectId(user_id)
    except:
        return jsonify({'error': 'Invalid user ID format'}), 400
    user_data = users_collection.find_one({'_id': user_id}, {'password': 0})
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    if isinstance(user_data, dict):
        user_data['_id'] = str(user_data['_id'])
        user_data['profile'] = str(user_data['profile'])
    return jsonify({'user': user_data}), 200 

@app.route('/users/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(user['profile'], ['update'], "users")
    try:
        user_id = ObjectId(user_id)
    except:
        return jsonify({'error': 'Invalid user ID format'}), 400
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    profile = data.get('profile', None)

    try:
        profile = ObjectId(profile)
    except:
        return jsonify({'error': 'Invalid profile ID format'}), 400

    if not username and not password and not profile:
        return jsonify({'message': 'Nothing to update'}), 400

    user_data = users_collection.find_one({'_id': user_id})
    if not user_data:
        return jsonify({'message': 'User not found'}), 404

    update_data = {}
    if username:
        update_data['username'] = username
    if password:
        # Encriptar la contraseña del usuario
        update_data['password'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if profile:
        update_data['profile'] = profile

    users_collection.update_one({'_id': user_id}, {'$set': update_data})
    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/users/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    user = users_collection.find_one({'username': current_user})
    
    # Verificar si el perfil del usuario tiene los permisos necesarios
    check_permissions(user['profile'], ['remove'], "users")
    try:
        user_id = ObjectId(user_id)
    except:
        return jsonify({'error': 'Invalid user ID format'}), 400
    result = users_collection.delete_one({'_id': user_id})
    if result.deleted_count == 1:
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404