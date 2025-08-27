from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from .models import User

PASSWORD_RULES = [
    Length(min=8, max=128, message="A senha deve ter entre 8 e 128 caracteres."),
    Regexp(r".*[A-Z].*", message="A senha deve ter ao menos 1 letra maiúscula."),
    Regexp(r".*[a-z].*", message="A senha deve ter ao menos 1 letra minúscula."),
    Regexp(r".*\d.*",   message="A senha deve ter ao menos 1 dígito."),  # <-- corrigido
    Regexp(r".*[^A-Za-z0-9].*", message="A senha deve ter ao menos 1 caractere especial."),
]

class RegisterForm(FlaskForm):
    name = StringField("Nome", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired(), *PASSWORD_RULES])
    password2 = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("password", message="As senhas não coincidem.")])
    submit = SubmitField("Criar conta")

    def validate_email(self, field):
        if User.query.filter(User.email == field.data.lower()).first():
            raise ValidationError("Este e-mail já está em uso.")

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar")
    submit = SubmitField("Entrar")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Senha atual", validators=[DataRequired()])
    new_password = PasswordField("Nova senha", validators=[DataRequired(), *PASSWORD_RULES])
    new_password2 = PasswordField("Confirmar nova senha", validators=[DataRequired(), EqualTo("new_password", message="As senhas não coincidem.")])
    submit = SubmitField("Alterar senha")
