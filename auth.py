from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import db as database
import bcrypt
import hmac

app = Flask(__name__)
client = database.init()
users_collection = client["users"]
app.config['JWT_SECRET_KEY'] = 'super-secret' # cambiar esto por una clave secreta real en producción
jwt = JWTManager(app)

# Modelo de usuario
class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        user_data = users_collection.find_one({'username': username})
        if user_data:
            return cls(user_data['username'], user_data['password'])
        return None

    @classmethod
    def find_by_id(cls, id):
        user_data = users_collection.find_one({'_id': id})
        if user_data:
            return cls(user_data['username'], user_data['password'])
        return None


def compare_digest(a, b):
    """
    Comparación de cadenas resistente a los ataques de temporización.
    """
    # Obtener la longitud de las cadenas para evitar comparaciones de longitud temprana.
    # Asegurarse de que ambas cadenas sean bytes.
    if len(a) != len(b) or not isinstance(a, bytes) or not isinstance(b, bytes):
        return False

    # Realizar la comparación byte a byte usando la función hmac.compare_digest.
    result = True
    for ai, bi in zip(a, b):
        result &= hmac.compare_digest(bytes([ai]), bytes([bi]))

    return result

# Funciones auxiliares para la autenticación
def authenticate(username, password):
    user = User.find_by_username(username)
    # Encriptar la contraseña del usuario y compara la con la contraseña almacenada
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return user
    else:
        return None

def identity(payload):
    user_id = payload['identity']
    return User.find_by_id(user_id)

# Endpoint para autenticar usuarios y generar tokens JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    user = authenticate(username, password)
    if user:
        access_token = create_access_token(identity=str(user.username))
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

# Proteger rutas con autenticación
@app.route('/protected')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'user': current_user}), 200