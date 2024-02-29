from flask_wtf import FlaskForm
from wtforms import StringField,EmailField,PasswordField,SubmitField,SearchField,SelectField,validators
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField,FileAllowed


class LoginForm(FlaskForm):
    email = EmailField(name="email",validators=[DataRequired()])
    password = PasswordField(name="password", validators=[DataRequired(),validators.Length(min=8,max=20)])
    submit = SubmitField("Let Me In!")



class SenOtp(FlaskForm):
    name = StringField(name="name", validators=[DataRequired(),validators.Length(min=3,max=20)])
    email = EmailField(name="email", validators=[DataRequired()])
    send_otp = SubmitField("Send otp")


class SignupForm(FlaskForm):
    name = StringField(name="name",validators=[DataRequired(),validators.Length(min=3,max=20)])
    email = EmailField(name="email", validators=[DataRequired()])
    opt = StringField(name="OTP",validators=[DataRequired()])
    password = PasswordField(name="password",validators=[DataRequired(),validators.Length(min=8,max=20)])
    confirm_password = PasswordField(name="confirm_password",validators=[DataRequired(),validators.Length(min=8,max=20)])
    signup = SubmitField("Signup")

class NewPost(FlaskForm):
    title = StringField(name="title",validators=[DataRequired(),validators.Length(max=250)])
    subtitle = StringField(name="subtitle",validators=[DataRequired(),validators.Length(max=250)])
    slug = StringField(name="slug",validators=[DataRequired(),validators.Length(max=250)])
    body = CKEditorField(name="blog content",validators=[DataRequired()])
    pic = FileField(name="picture",validators=[FileAllowed(upload_set=["png","webp","gif","jpg","jpeg"])])
    submit = SubmitField("submit")

class CommentForm(FlaskForm):
    comment_text = CKEditorField(name="comments",validators=[DataRequired()])
    submit = SubmitField("submit")

class SearchForm(FlaskForm):
    search = SearchField(name="search",render_kw={"placeholder": "search"})
    submit = SubmitField(name="search")

class CreateThread(FlaskForm):
    title = StringField(name="title",validators=[DataRequired(),validators.Length(max=250)])
    brief = CKEditorField(name="brief",validators=[DataRequired(),validators.Length(max=250)])
    categories = SelectField(name="categories", choices=[('general', 'general'), ('Education', 'education'), ('Sports','sports')])
    hashtags = StringField(name="hashtags",validators=[DataRequired(),validators.Length(max=250)])
    submit = SubmitField(name="create")







