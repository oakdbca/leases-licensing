from django.contrib.auth import get_user_model
from django.forms import CharField, DateField, EmailField, Form

User = get_user_model()


class LoginForm(Form):
    email = EmailField(max_length=254)


class FirstTimeForm(Form):
    """Not sure if this is needed but it was imported in leaseslicensing/views.py so adding for now"""

    redirect_url = CharField()
    first_name = CharField()
    last_name = CharField()
    dob = DateField(input_formats=["%d/%m/%Y"])
