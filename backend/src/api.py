import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
    Validate JSON request
    This is a function to verify if the JSON payload contains the required fields.
'''


def validate_request(required_fields, data):
    if not data:
        return 'data'
    for f in required_fields:
        try:
            data[f]
        except:
            return f


'''
    Validate if the json payload contains valid drink information
'''


def validate_drink_json(data):
    expected = ['title', 'recipe']
    missing_fields = validate_request(expected, data)
    if missing_fields:
        abort(422, f'Request is missing the following fields: {missing_fields}')

    # Recipe should be array of object
    if not isinstance(data['recipe'], list):
        abort(422, f'The request field recipe must be of array type')

    # Recipe should contain name color and parts
    expected = ['name', 'color', 'parts']
    for recipe in data['recipe']:
        missing_fields = validate_request(expected, recipe)
        if missing_fields:
            abort(422, f'Request is missing the following fields in the recipe: {missing_fields}')


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''



@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    response = {
        "Success": True,
        "drinks": [c.short() for c in drinks]
    }
    return jsonify(response), 200


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
def get_drink_details(payload):
    drinks = Drink.query.all()
    response = {
        "Success": True,
        "drinks": [c.long() for c in drinks]
    }
    return jsonify(response), 200


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
def post_drink_details(payload):
    request_body = request.json
    # Post data validations.
    # @TODO Better use marshmallow for request serialization
    # drink should contain title and recipes
    validate_drink_json(request_body)

    # Add the data to database
    try:
        drink = Drink(title=request_body['title'], recipe=json.dumps(request_body['recipe']))
        drink.insert()
    except IntegrityError:
        abort(422, f'drink with name {request_body["title"]} is already existed')
    response = {
        "Success": True,
        "drinks": [{
            "id": drink.id,
            "title": request_body["title"],
            "recipe": request_body["recipe"]
        }]
    }
    # @TODO: This should returns 201
    return jsonify(response), 200


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


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink_details(payload, id=None):
    drink = Drink.query.get(id)
    if drink == None:
        abort(404, f'drink {id} does not exist')

    request_body = request.json

    drink_resp = {}
    try:
        if 'title' in request_body:
            drink.title = request_body['title']
        if 'recipe' in request_body:
            recipe = request_body['recipe']
            if not isinstance(recipe, list):
                abort(422, f'The request field recipe must be of array type')
            expected = ['name', 'color', 'parts']
            missing_fields = validate_request(expected, recipe)
            if missing_fields:
                abort(422, f'Request is missing the following fields in the recipe: {missing_fields}')
            drink.recipe = json.dumps(request_body['recipe'])
        drink.update()
    except Exception as e:
        print(e)
        abort(500)

    response = {
        "Success": True,
        "drinks": [{
            "id": drink.id,
            "title": drink.title,
            "recipe": json.loads(drink.recipe)
        }]
    }
    return jsonify(response), 200


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


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_details(payload, id=None):
    drink = Drink.query.get(id)
    if drink == None:
        abort(404, f'drink {id} does not exist')
    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(500)

    response = {
        "Success": True,
        "delete": id
    }
    return jsonify(response), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error="request cannot be processed"):
    return jsonify({
        "success": False,
        "error": 422,
        "message": str(error)
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthenticated(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthenticated user"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "You do not have a sufficient privilege to perform this action"
    }), 403
