from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

# Model for Post creation form
class PostForm(FlaskForm):
    post_title = StringField('Post Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Post Text', validators=[DataRequired()])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    comment_text = TextAreaField('Comment', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Post Comment')
