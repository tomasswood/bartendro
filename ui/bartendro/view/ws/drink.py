# -*- coding: utf-8 -*-
import json
from time import sleep
from operator import itemgetter
from bartendro import app, db, mixer
from flask import Flask, request
from flask.ext.login import login_required, current_user
from werkzeug.exceptions import ServiceUnavailable, BadRequest
from bartendro.model.drink import Drink
from bartendro.model.drink_name import DrinkName
from bartendro.model.booze import Booze
from bartendro.model.users import Users
from bartendro.model.drink_booze import DrinkBooze

def ws_make_drink(drink, recipe, speed = 255):
	drink_mixer = app.mixer
	try:
		err = drink_mixer.make_drink(drink, recipe, speed)
		if not err:
			return "ok\n"
		else:
			raise BadRequest(err)
	except mixer.BartendroBusyError:
		raise ServiceUnavailable("busy")

@app.route('/ws/drink/<int:drink>/<int:user>/<int:drink_price>')
def ws_drink(drink,user,drink_price):

	db.session.query(Users).filter(Users.id==user).update({'credit' : drink_price})
	db.session.flush()
	db.session.commit()

	drink_mixer = app.mixer
	if app.options.must_login_to_dispense and not current_user.is_authenticated():
		return "login required"

	recipe = {}
	for arg in request.args:
		recipe[arg] = int(request.args.get(arg))
		admin_users_creditupdate()
	try:
		err = drink_mixer.make_drink(drink, recipe)
		if not err:
			return "ok\n"
		else:
			raise BadRequest(err)
	except mixer.BartendroBusyError:
		raise ServiceUnavailable("busy")

@app.route('/ws/drink/<int:drink>/speed/<int:speed>')
def ws_drink_at_speed(drink, speed):
	if app.options.must_login_to_dispense and not current_user.is_authenticated():
		return "login required"

	recipe = {}
	for arg in request.args:
		recipe[arg] = int(request.args.get(arg))

	return ws_make_drink(drink, recipe, speed)

@app.route('/ws/drink/<int:drink>/available/<int:state>')
def ws_drink_available(drink, state):
	if not drink:
		db.session.query(Drink).update({'available' : state})
	else:
		db.session.query(Drink).filter(Drink.id==drink).update({'available' : state})
	db.session.flush()
	db.session.commit()
	return "ok\n"

@app.route('/ws/drink/<int:id>/load')
@login_required
def admin_drink_load(id):
	drink = Drink.query.filter_by(id=int(id)).first()
	boozes = []
	for booze in drink.drink_boozes:
		boozes.append((booze.booze_id, booze.value))
	drink = { 
		'id'         : id,
		'name'       : drink.name.name,
		'desc'       : drink.desc,
		'popular'    : drink.popular,
		'available'  : drink.available,
		'boozes'     : boozes,
		'num_boozes' : len(boozes)
	}
	return json.dumps(drink)

@app.route('/ws/drink/<int:drink>/save', methods=["POST"])
def ws_drink_save(drink):

	data = request.json['drink']
	id = int(data["id"] or 0)
	if id > 0:
		drink = Drink.query.filter_by(id=int(id)).first()
	else:
		id = 0
		drink = Drink()
		db.session.add(drink)

	try:
		drink.name.name = data['name']
		drink.desc = data['desc']
		if data['popular']:
			drink.popular = True
		else:
			drink.popular = False
			
		if data['available']:
			drink.available = True
		else:
			drink.available = False
	except ValueError:
		raise BadRequest

	for selected_booze_id, parts, old_booze_id in data['boozes']:
		try:
			selected_booze_id = int(selected_booze_id) # this is the id that comes from the most recent selection
			old_booze_id = int(old_booze_id)     # this id is the id that was previously used by this slot. Used for
												 # cleaning up or updateing existing entries
			parts = int(parts)                   
		except ValueError:
			raise BadRequest

		# if the parts are set to zero, remove this drink_booze from this drink
		if parts == 0:
			if old_booze_id != 0:
				for i, dbooze in enumerate(drink.drink_boozes):
					if dbooze.booze_id == old_booze_id:
						db.session.delete(drink.drink_boozes[i])
						break
			continue

		# if there is an old_booze_id, then update the existing entry
		if old_booze_id > 0:
			for drink_booze in drink.drink_boozes:
				if old_booze_id == drink_booze.booze_id:
					drink_booze.value = parts
					if (selected_booze_id != drink_booze.booze_id):
						drink_booze.booze = Booze.query.filter_by(id=selected_booze_id).first()
					break
		else:
			# Create a new drink-booze entry
			booze = Booze.query.filter_by(id=selected_booze_id).first()
			DrinkBooze(drink, booze, parts, 0)

	db.session.commit()
	mc = app.mc
	mc.delete("top_drinks")
	mc.delete("other_drinks")
	mc.delete("available_drink_list")

	return json.dumps({ 'id' : drink.id });
