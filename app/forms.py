from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
	id = StringField('id', validators = [DataRequired()])
	title = StringField('title', validators = [DataRequired()])

