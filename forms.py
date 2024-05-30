from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

class PostForm(FlaskForm):
    post_title = StringField('Post Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Post Text', validators=[DataRequired()])
    submit = SubmitField('Create Post')