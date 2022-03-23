from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from . import db

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Base):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'MODERATOR': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'ADMINISTRATOR': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN]
        }

        default_role = 'User'
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)

        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return "Role: {}".format(self.name)

class User(db.Base, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64),default="")
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        """ Esta tabla y sus funciones proporcionarán la asignación de permisos que necesitamos para
        nuestra aplicación, asegurándonos de que nuestros usuarios solo puedan acceder a las cosas a
        las que deberían tener acceso y permitiéndonos crear funciones para que nuestros moderadores
        y administradores editen contenido cuestionable y arranquen. usuarios tóxicos!"""

        super(User, self).__init__(**kwargs)
        if self.role is None:
            # Comprobar si el nuevo usuario está establecido como el admin y darle los permisos de admin
            if self.email == current_app.config['OFFBRAND_ADMIN']:
                self.role = db.session.query(Role).filter_by(name='Administrator').first()
            if self.role is None:
                self.role = db.session.query(Role).filter_by(default=True).first()
            if self.email is not None and self.avatar_hash is None:
                self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.id:
            return False

        self.confirmed = True

        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset':self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiraiton=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiraiton)
        return s.dumps({'change_email':self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self,token):
        s = Serializer(current_app['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')

        if new_email is None:
            return False

        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)

        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
                                                                     hash=hash,
                                                                     size=size,
                                                                     default=default,
                                                                     rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    """
    En este momento, si se realiza una verificación de permisos en un usuario que no tiene una cuenta,
    obtendremos un pequeño error desagradable.

    Clase para usuarios anónimos.
    """
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

class ClasificadorTareasABC(db.Base):
    """
    Modelo que define la clasificación de tareas disponibles en la base de datos.

    SISTEMA ABC:
        (A) Son aquellas imprescindibles para la consecución de los objetivos planteados. Serían pues, las más
        importantes en nuestro puesto de trabajo y a las que deberíamos dedicar la mayor parte de nuestros esfuerzos.
        Son tareas que no podemos delegar y tienen el mayor valor respecto de los objetivos de nuestro trabajo.

        Por ejemplo, y en general, concertar las citas de nuestro directivo, hacer una llamada en su nombre para
        conseguir una reunión, recibir en su ausencia a un contacto… forman parte de nuestro cometido como
        asistentes de dirección.

        (B) No estando ligadas directamente a los objetivos, nos ayudan a llegar a ellos. Serían las segundas en
        importancia y en ocasiones, podemos delegarlas. Por ejemplo, buscar una información necesaria para nuestro
        jefe, que podemos pedir que nos prepare otro departamento u otra persona.

        (C) Tareas que no nos aportan nada en relación a los objetivos. Ello no significa que no deban hacerse,
        sino que respecto a las responsabilidades de nuestro puesto no son tan relevantes. Son las que deberíamos
        acometer en último lugar e incluso delegar si tenemos la oportunidad de hacerlo. No son estratégicas para
        nosotros ni aportan valor a nuestro puesto de trabajo ni al directivo al que prestamos servicio.
        Sin embargo, suelen ser las que nos quitan gran parte de nuestro tiempo: trabajos rutinarios, teléfono,
        tareas administrativas…)

    Fuente: http://www.topsecretaria.com/el-sistema-abc-de-clasificacion-de-tareas/
    """
    __tablename__ = 'clasificador_tareas'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10))
    descripcion = db.Column(db.Text, nullable=False)
    ponderacion = db.Column(db.Integer, default=10)

    def __init__(self, **kwargs):
        super(ClasificadorTareasABC, self).__init__(**kwargs)

    @staticmethod
    def insert_clasificador():
        clasificacion_tareas = {
            'A': ['Muy Importante',
                  "Son aquellas imprescindibles para la consecución de los objetivos planteados. Serían pues, las más \
                  importantes en nuestro puesto de trabajo y a las que deberíamos dedicar la mayor parte de nuestros \
                  esfuerzos.",
                  70],
            'B': ['Importante',
                  'No estando ligadas directamente a los objetivos, nos ayudan a llegar a ellos. Serían las segundas \
                  en importancia y en ocasiones, podemos delegarlas.',
                  20],
            'C': ['Poco importantes',
                  'Tareas que no nos aportan nada en relación a los objetivos. Ello no significa que no deban hacerse, \
                  sino que respecto a las responsabilidades de nuestro puesto no son tan relevantes. Son las que \
                  deberíamos acometer en último lugar e incluso delegar si tenemos la oportunidad de hacerlo. No son \
                  estratégicas para nosotros ni aportan valor a nuestro puesto de trabajo ni al directivo al que \
                  prestamos servicio. Sin embargo, suelen ser las que nos quitan gran parte de nuestro tiempo: \
                  trabajos rutinarios, teléfono, tareas administrativas…)',
                  10]
        }

        for ct in clasificacion_tareas:
            tarea = db.session.query(ClasificadorTareasABC).filter_by(tipo=ct).first()
            if tarea is None:
                # Añadir tarea completa a la base de datos.
                tarea = ClasificadorTareasABC(tipo=ct,
                                              descripcion=clasificacion_tareas[ct][1],
                                              ponderacion=clasificacion_tareas[ct][2])
                db.session.add(tarea)
        db.session.commit()

# Modelos de aplicaciones python en web
class Task(db.Base, UserMixin):
    """
    Clase Task (Tarea). Modelo de datos de una tarea del manager app

    Actualización 1 (no realizada): Añadir tipo de tarea como tabla en la bbdd
    """
    __tablename__ = "manager"
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    usuario = db.Column(db.Integer, db.ForeignKey('users.id')) # Id del usuario (tabla users)
    tarea = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), db.ForeignKey('clasificador_tareas.tipo'), nullable=False)  # Tipo de tarea (Clasificación ABC).
    tiempo_empleado = db.Column(db.Float)  # Tiempo dedicado a la tarea (Floatante)
    duracion_total = db.Column(db.Float)   # Duración en horas total de la tarea (Floatante)
    finalizada = db.Column(db.Boolean)     # Booleano que indica si la tarea ha sido realizada o no
    fecha_inicio = db.Column(db.String()) # Fecha de inicio
    fecha_final  = db.Column(db.String()) # Fecha final prevista (deadline).

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)

    def __repr__(self):
        return "Tarea: {}. Usuario: {}. Descripcion: {}. Clasificacion: {}. Tiempo_empleado: {} horas. " \
               "Duracion: {} horas. Finalizada: {}. Fecha Inicio: {}. Fecha final: {}".format(self.id,
                                                                                              self.usuario,
                                                                                              self.descripcion,
                                                                                              self.clasificacion,
                                                                                              self.tiempo_empleado,
                                                                                              self.duracion_total,
                                                                                              self.finalizada,
                                                                                              self.fecha_inicio,
                                                                                              self.fecha_final)

    def __str__(self):
        return "Tarea: {}. Usuario: {}. Descripcion: {}. Clasificacion: {}. Tiempo_empleado: {} horas. " \
               "Duracion: {} horas. Finalizada: {}. Fecha Inicio: {}. Fecha final: {}".format(self.id,
                                                                                              self.usuario,
                                                                                              self.descripcion,
                                                                                              self.clasificacion,
                                                                                              self.tiempo_empleado,
                                                                                              self.duracion_total,
                                                                                              self.finalizada,
                                                                                              self.fecha_inicio,
                                                                                              self.fecha_final)



