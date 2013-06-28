# -*- coding: utf-8 -*-
from bartendro import app, db
from flask import Flask, request, jsonify
from bartendro.model.drink import Drink
from bartendro.model.users import Users
from bartendro.form.users import UsersForm

@app.route('/ws/users/match/<str>')
def ws_users(request, str):
    str = str + "%%"
    users = db.session.query("id", "username").from_statement("SELECT id, username FROM users WHERE username LIKE :s").params(s=str).all()
    return jsonify(users)
