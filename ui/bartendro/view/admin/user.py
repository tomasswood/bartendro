# -*- coding: utf-8 -*-
from bartendro import app, db, login_manager
from bartendro.form.login import LoginForm
from flask import Flask, request, render_template, flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user
from bartendro.model.users import Users

class User(object):
    id = 0
    credit = 0
    username = ""
    administrator = False

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return self.username != ""

    def is_active(self):
        return True

    def is_anonymous(self):
        return self.username == ""

    def is_administrator(self):
        dbAdmin = db.session.query(Users).filter(Users.username == self.username).first()
        if (dbAdmin.administrator == 1):
            self.administrator = True
        else:
            self.administrator = False
        return self.administrator

    def get_id(self):
        return self.username

    def get_username(self):
        return self.username

    def __repr__(self):
        return '<User %d>' % self.username

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form.get("user" or '')
        password = request.form.get("password" or '')
        dbUser = db.session.query(Users).filter(Users.username == username, Users.password == password).first()
        if dbUser is not None:
            loginUser = dbUser.username
            loginPassword = dbUser.password
            if (dbUser.administrator == 1):
                administrator = True
            if (username == loginUser and password == loginPassword):
                login_user(User(username))
                return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid login.")
    return render_template("/admin/login", form=form)

@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
