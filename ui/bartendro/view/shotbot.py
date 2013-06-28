# -*- coding: utf-8 -*-
import memcache
from bartendro import app, db
from flask import Flask, request, render_template
from flask.ext.login import login_required
from bartendro.model.drink import Drink
from bartendro.model.drink_name import DrinkName
from bartendro.view import root_menu

@app.route('/shotbot')
@login_required
def index(request):
    user = root_menu.index_layout()
    return render_template("shotbot", title="ShotBot!",user=user)
