from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager
from bson.objectid import ObjectId
import db as database

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
client = database.init()
profiles_collection = client["profiles"]
jwt = JWTManager(app)

class Profile:
    def __init__(self, name, permissions, _id=None):
        self.name = name
        self.permissions = permissions
        self._id = _id

    def save(self):
        if not self._id:
            self._id = str(profiles_collection.insert_one({
                'name': self.name,
                'permissions': self.permissions
            }).inserted_id)

    def update(self, new_name=None, new_permissions=None):
        update_data = {}
        if new_name:
            update_data['name'] = new_name
        if new_permissions:
            update_data['permissions'] = new_permissions
        profiles_collection.update_one({'_id': ObjectId(self._id)}, {'$set': update_data})

    def delete(self):
        profiles_collection.delete_one({'_id': ObjectId(self._id)})

    @staticmethod
    def find_by_id(profile_id):
        profile = profiles_collection.find_one({'_id': ObjectId(profile_id)})
        if profile:
            return Profile(
                name=profile['name'],
                permissions=profile['permissions'],
                _id=str(profile['_id'])
            )
        else:
            return None

    @staticmethod
    def find_all():
        profiles = profiles_collection.find()
        result = []
        for profile in profiles:
            result.append(Profile(
                name=profile['name'],
                permissions=profile['permissions'],
                _id=str(profile['_id'])
            ))
        return result

# Endpoint para crear un nuevo perfil
@app.route('/profiles', methods=['POST'])
@jwt_required()
def create_profile():
    data = request.get_json()
    name = data.get('name', None)
    permissions = data.get('permissions', [])

    if not name:
        return jsonify({'message': 'Name is required'}), 400

    profile = Profile(name=name, permissions=permissions)
    profile.save()
    print(profile)

    return jsonify({'message': 'Profile created successfully', 'profile': {
        'name': profile.name,
        'permissions': profile.permissions,
        'id': str(profile._id)
    }}), 201

# Endpoint para obtener un perfil por ID
@app.route('/profiles/<string:profile_id>', methods=['GET'])
@jwt_required()
def get_profile(profile_id):
    profile = Profile.find_by_id(profile_id)
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    return jsonify({
       'name': profile.name,
       'permissions': profile.permissions,
       'id': profile._id
   }), 200

@app.route('/profiles/<string:profile_id>', methods=['PUT'])
@jwt_required()
def update_profile(profile_id):
    data = request.get_json()
    new_name = data.get('name', None)
    new_permissions = data.get('permissions', None)
    profile = Profile.find_by_id(profile_id)
    if not profile:
       return jsonify({'message': 'Profile not found'}), 404

    profile.update(new_name=new_name, new_permissions=new_permissions)

    return jsonify({'message': 'Profile updated successfully', 'profile': {
       'name': new_name if new_name else profile.name,
       'permissions': new_permissions if new_permissions else profile.permissions,
       'id': profile._id
    }}), 200

@app.route('/profiles/<string:profile_id>', methods=['DELETE'])
@jwt_required()
def delete_profile(profile_id):
    profile = Profile.find_by_id(profile_id)
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    profile.delete()
    return jsonify({'message': 'Profile deleted successfully'}), 200
    
@app.route('/profiles', methods=['GET'])
@jwt_required()
def list_profiles():
    profiles = Profile.find_all()
    result = []
    for profile in profiles:
        result.append({
            'name': profile.name,
            'permissions': profile.permissions,
            'id': profile._id
        })
    return jsonify({'profiles': result}), 200

def check_permissions(profile_id, required_permissions):
    profile = Profile.find_by_id(profile_id)
    if not profile:
        # El perfil del usuario no existe
        raise ValueError('Invalid profile ID')
    if not all(p in profile.permissions for p in required_permissions):
        # El perfil del usuario no tiene los permisos necesarios
        raise ValueError('Insufficient permissions')