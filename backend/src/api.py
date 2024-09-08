import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getting_all_drinks():
    allDrinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [dri.short() for dri in allDrinks]
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks_details(payload):
    allDrinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [dri.long() for dri in allDrinks]
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def adding_new_drink(payload):
    req = request.get_json()

    try:
        req_details = req['recipe']
        if isinstance(req_details, dict):
            req_details = [req_details]

        dri = Drink()
        dri.title = req['title']
        dri.recipe = json.dumps(req_details)  # convert object to a string
        dri.insert()

    except BaseException:
        abort(400)

    return jsonify(
        {'success': True, 
         'drinks': [dri.long()]})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updating_drink_details(payload, id):
    req = request.get_json()
    dri = Drink.query.filter(Drink.id == id).one_or_none()

    if not dri:
        abort(404)

    try:
        drink_title = req.get('title')
        drink_recipe = req.get('recipe')
        if drink_title:
            dri.title = drink_title

        if drink_recipe:
            dri.recipe = json.dumps(req['recipe'])

        dri.update()
    except BaseException:
        abort(400)

    return jsonify(
        {'success': True, 
         'drinks': [dri.long()]
         }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def removing_drink(payload, id):
    dri = Drink.query.filter(Drink.id == id).one_or_none()

    if not dri:
        abort(404)

    try:
        dri.delete()
    except BaseException:
        abort(400)

    return jsonify(
        {'success': True, 
         'delete': id}
         ), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def drink_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Drink is not available in application"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "Authentication Failed check Username, Password and JWT token"
    }), error.status_code
