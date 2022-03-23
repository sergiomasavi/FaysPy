from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import manager_app
from ..models import User, Task, ClasificadorTareasABC
from ..email import send_email
from .. import db
from .forms import *
"""
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
"""

@manager_app.route('/notebook', methods=['GET', 'POST'])
def notebook():    # Get data from form
    form = ManagerForm()
    # Validate user input
    if form.validate_on_submit(): # forms.py --> ∫validate_email() & validate_username()
        if form.data['fecha_inicio'] > form.data['fecha_final']:
            flash('Introduce correctamente las fechas de inicio y fin de la actividad')
        else:
            tarea =  Task(usuario = current_user.id,
                          tarea = form.data['tarea'].title(),
                          tipo = form.data['tipo'],
                          tiempo_empleado = 0,
                          duracion_total = form.data['duracion_total'],
                          finalizada=False,
                          fecha_inicio = form.data['fecha_inicio'],
                          fecha_final  = form.data['fecha_final'])
            db.session.add(tarea)
            db.session.commit()
            return redirect(url_for('manager_app.notebook'))

    return render_template('manager/notebook.html', form=form)

@manager_app.route('/agenda', methods=['GET', 'POST'])
def agenda():
    form = AgendaForm()

    # Obtener lista de tareas del usuario de la base de datos
    tareas = db.session.query(Task).filter_by(usuario=current_user.id).all()

    return render_template('manager/agenda.html', form=form, lista_tareas=tareas)

@manager_app.route('/agenda/update/id=<id>', methods=['GET','POST'])
def agenda_update(id):
    form = AgendaForm()
    # Obtener tarea a actualizar
    tarea = db.session.query(Task).filter_by(id=id).first()

    # Obtener lista de tareas del usuario de la base de datos
    tareas = db.session.query(Task).filter_by(usuario=current_user.id).all()

    # Modificar tarea de la bbdd si se ha producido algún cambio
    if tarea:
        modificada = False
        if tarea.tiempo_empleado != form.data['tiempo_empleado']:
            tarea.tiempo_empleado = form.data['tiempo_empleado']
            modificada = True

        if tarea.finalizada != form.data['finalizada']:
            tarea.finalizada = form.data['finalizada']
            modificada=True

        if modificada:
            db.session.commit()



    return redirect(url_for('manager_app.agenda'))

@manager_app.route('/agenda/delete/id=<id>', methods=['GET','POST'])
def agenda_delete(id):
    # Eliminar tarea
    tarea = db.session.query(Task).filter_by(id=int(id)).delete()

    # Ejecutar operaciones sobre la bbdd
    db.session.commit()

    return redirect(url_for('manager_app.agenda'))

