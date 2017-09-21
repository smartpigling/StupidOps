from wtforms import Form, StringField, TextAreaField
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextAreaFieldWidget
from flask_appbuilder.forms import DynamicForm


class NotepadForm(DynamicForm):
    context = TextAreaField('内容', widget=BS3TextAreaFieldWidget())