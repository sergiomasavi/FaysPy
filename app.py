import os
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Role, Permission, ClasificadorTareasABC, Task

# Instanciar/Crear apicación
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Añadir tabla de roles de usuario (si no existe)
#Role.insert_roles()

# Añadir tabla clasificador tareas (si no existe)
#ClasificadorTareasABC.insert_clasificador()

# Migración 1
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                User=User,
                Role=Role,
                Permission=Permission,
                ClasificadorTareasABC=ClasificadorTareasABC,
                Task=Task)

@app.cli.command()
def deploy():
    """ Arrancar todas las operaciones de desarrollo. """
    # Migrar la bbdd a la última versión
    upgrade()

    # Crear o actualizar roles de usuario
    Role.insert_roles()

if __name__ == '__main__':
    app.run(debug=True, port=5500)