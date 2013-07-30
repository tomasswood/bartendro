#!/usr/bin/env python
from wtforms import Form, TextField, DecimalField, HiddenField, validators, \
                          TextAreaField, SubmitField, SelectField
from bartendro.model import users

class UsersForm(Form):
    id = HiddenField(u"id", default=0)
    username = TextField(u"Username", [validators.Length(min=3, max=25)])
    password = TextField(u"Password", [validators.Length(min=3, max=25)])
    credit = DecimalField(u"Credit", [validators.NumberRange(0, 10000)], default=0, places=0)
    administrator = DecimalField(u"Administrator", [validators.NumberRange(0, 1)], default=0, places=0)
    superadministrator = DecimalField(u"Super Administrator", [validators.NumberRange(0, 1)], default=0, places=0)
    save = SubmitField(u"Save")
    cancel = SubmitField(u"Cancel")

form = UsersForm()
