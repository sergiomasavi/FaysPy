from flask import Blueprint

# Crear plano de autorización de la aplicación
manager_app = Blueprint('manager_app',__name__)

# Importar vistas del plano
from . import views