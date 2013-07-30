# -*- coding: utf-8 -*-
from bartendro import app, db
from flask import Flask, request, redirect, render_template
from flask.ext.login import login_required
from bartendro.model.users import Users
from bartendro.form.users import UsersForm

@app.route('/admin/users')
@login_required
def admin_users():
    form = UsersForm(request.form)
    users = Users.query.order_by(Users.id)
    return render_template("admin/users", options=app.options, users=users, form=form, title="Users")

@app.route('/admin/users/edit/<id>')
@login_required
def admin_users_edit(id):
    saved = int(request.args.get('saved', "0"))
    user = Users.query.filter_by(id=int(id)).first()
    form = UsersForm(obj=user)
    users = Users.query.order_by(Users.id)
    return render_template("admin/users", options=app.options, user=user, users=users, form=form, title="Users", saved=saved)

@app.route('/admin/users/save', methods=['POST'])
@login_required
def admin_users_save():

    cancel = request.form.get("cancel")
    if cancel: return redirect('/admin/users')

    form = UsersForm(request.form)
    if request.method == 'POST' and form.validate():
        id = int(request.form.get("id") or '0')
        if id:
            user = Users.query.filter_by(id=int(id)).first()
            user.update(form.data)
        else:
            user = Users(data=form.data)
            db.session.add(user)

        db.session.commit()
        return redirect('/admin/users/edit/%d?saved=1' % user.id)

    users = Users.query.order_by(Users.id)
    return render_template("admin/users", options=app.options, users=users, form=form, title="")
