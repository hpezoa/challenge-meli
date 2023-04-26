from flask import Flask
from flask_jwt_extended import JWTManager
from threading import Thread
from auth import app as auth_app
from users import app as users_app
from profiles import app as profiles_app
from external import app as external_app

# Crear una aplicación Flask maestra para ejecutar las aplicaciones de autenticación y CRUD en diferentes subprocesos.
master_app = Flask(__name__)

# Configurar la clave secreta JWT
master_app.config['JWT_SECRET_KEY'] = 'super-secret'

# Inicializar el administrador de JWT
jwt = JWTManager(master_app)

# Definir la función para ejecutar la aplicación Flask en un subproceso
def run_app(app,port):
    app.run(port=port)

# Ejecutar las aplicaciones de autenticación y CRUD en diferentes subprocesos dentro de la misma aplicación Flask
auth_thread = Thread(target=run_app, args=[auth_app,5000])
auth_thread.start()
crud_thread = Thread(target=run_app, args=[users_app,8000])
crud_thread.start()
crud_thread = Thread(target=run_app, args=[profiles_app,8001])
crud_thread.start()
crud_thread = Thread(target=run_app, args=[external_app,8002])
crud_thread.start()

# Ejecutar la aplicación maestra Flask
if __name__ == '__main__':
    master_app.run()
