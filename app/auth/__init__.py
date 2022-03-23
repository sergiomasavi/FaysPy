from flask import Blueprint

# Crear plano de autorización de la aplicación
auth = Blueprint('auth',__name__)

# Importar vistas del plano
from . import views