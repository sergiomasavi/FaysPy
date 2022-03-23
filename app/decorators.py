"""
Una vez se tiene la tabla Permisos y las funciones configuradas, se debe configurar
una función decorator que verifique los permisos específicos para una ruta.

Para ello, se crea el archivo decorator.py en el directorio de la aplicación.
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    """ El primer decorador permite establecer un nivel específico de permisos necesarios para
        acceder a una ruta o función, mientras que el segundo se utiliza para verificar que el usuario tiene
        permisos de nivel de administrador.
    """
    def decorator(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if not current_user.can(permission):
               abort(403)
           return f(*args, **kwargs)
       return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)