# -*- coding: utf-8 -*-
from time import sleep
from bartendro import app, db
from flask import Flask, request
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import ServiceUnavailable
from bartendro.model.drink import Drink
from bartendro.model.booze import Booze
from bartendro.model.users import Users
from bartendro.form.booze import BoozeForm
from bartendro import constant

@app.route('/ws/drink/<int:drink>/<int:user>/<int:drink_price>')
def ws_drink(drink,user,drink_price):

    db.session.query(Users).filter(Users.id==user).update({'credit' : drink_price})
    db.session.flush()
    db.session.commit()

    mixer = app.mixer

    if app.options.must_login_to_dispense and not current_user.is_authenticated():
        return "login required"

    recipe = {}
    for arg in request.args:
        recipe[arg] = int(request.args.get(arg))
        admin_users_creditupdate()
    if mixer.make_drink(drink, recipe):
        return "ok\n"
    else:
        raise ServiceUnavailable("Error: %s (%d)" % (mixer.get_error(), ret))

@app.route('/ws/drink/<int:drink>/available/<int:state>')
def ws_drink_available(drink, state):

    if not drink:
        db.session.query(Drink).update({'available' : state})
    else:
        db.session.query(Drink).filter(Drink.id==drink).update({'available' : state})
    db.session.flush()
    db.session.commit()
    return "ok\n"
