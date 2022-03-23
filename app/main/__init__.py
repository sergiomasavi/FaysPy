# Crear el plano (blueprint)
from flask import Blueprint

# Crear plano de autorización de la aplicación
main = Blueprint('main',__name__)

# Importar vistas del plano
from . import views