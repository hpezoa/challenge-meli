
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

def init():
    # Configuración de la conexión a MongoDB
    client = MongoClient("mongodb+srv://aasm89:mufOibdlaX6FQZRy@cluster0.gcreiub.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where(), server_api=ServerApi('1'))
    db = client['challenge']
    return db