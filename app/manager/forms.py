from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms.fields.html5 import DateField
from wtforms import ValidationError
from ..models import User
from .. import db

class ManagerForm(FlaskForm):

    tarea = StringField('Tarea', validators=[DataRequired()])
    tipo = StringField('Tipo', validators=[DataRequired()])
    duracion_total = FloatField('Tiempo', validators=[DataRequired()])
    fecha_inicio = DateField('Inicio')
    fecha_final = DateField('Fin')
    submit = SubmitField('Submit')

class AgendaForm(FlaskForm):
    tiempo_empleado = FloatField('Tiempo empleado')
    finalizada = BooleanField('Finalizada')
    submit = SubmitField('Submit')

