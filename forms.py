from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

# Model for Post creation form
class PostForm(FlaskForm):
    post_title = StringField('Post Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Post Text', validators=[DataRequired()])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    comment_text = TextAreaField('', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})
