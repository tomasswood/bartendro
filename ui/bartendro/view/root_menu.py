# -*- coding: utf-8 -*-
import memcache
from bartendro import app, db
from flask import Flask, request, render_template
from flask.ext.login import login_required, current_user
from bartendro.model.users import Users
from bartendro.view.admin.user import User

def index_layout():
	user = db.session.query(Users).filter(Users.username == current_user.username).first()
	return user