from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker

# Instanciar dependencias externas como objetos de la aplicación Python
moment = Moment()
mail = Mail()
login_manager = LoginManager()
bootstrap = Bootstrap()
datepicker = datepicker()
