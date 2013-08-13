# -*- coding: utf-8 -*-
import memcache
from sqlalchemy import func, asc
from bartendro import app, db
from flask import Flask, request, render_template
from flask.ext.login import login_required
from bartendro.model.dispenser import Dispenser
from bartendro.model.drink import Drink
from bartendro.model.drink_name import DrinkName
from bartendro.view import root_menu

@login_required
def process_ingredients(drinks):
    for drink in drinks:
        drink.process_ingredients()

@login_required
def filter_drink_list(can_make_dict, drinks):
    filtered = []
    for drink in drinks:
        try:
            foo =can_make_dict[drink.id]
            filtered.append(drink)
        except KeyError:
            pass
    return filtered

@app.route('/')
@login_required
def index():
    if app.mixer.disp_count == 1:
        disp = db.session.query(Dispenser) \
                          .filter(Dispenser.id == 1) \
                          .one()
        return render_template("shotbot", booze=disp.booze.name, title="ShotBot")

    can_make = app.mixer.get_available_drink_list()
    can_make_dict = {}
    for drink in can_make:
        can_make_dict[drink] = 1

    top_drinks = db.session.query(Drink) \
                        .join(DrinkName) \
                        .filter(Drink.name_id == DrinkName.id)  \
                        .filter(Drink.popular == 1)  \
                        .filter(Drink.available == 1)  \
                        .order_by(asc(func.lower(DrinkName.name))).all() 
    top_drinks = filter_drink_list(can_make_dict, top_drinks)
    process_ingredients(top_drinks)

    other_drinks = db.session.query(Drink) \
                        .join(DrinkName) \
                        .filter(Drink.name_id == DrinkName.id)  \
                        .filter(Drink.popular == 0)  \
                        .filter(Drink.available == 1)  \
                        .order_by(asc(func.lower(DrinkName.name))).all() 
    other_drinks = filter_drink_list(can_make_dict, other_drinks)
    process_ingredients(other_drinks)
    user = root_menu.index_layout()
    return render_template("index", 
                           top_drinks=top_drinks, 
                           other_drinks=other_drinks,
                           title="Bartendro", user=user)
