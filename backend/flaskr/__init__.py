import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

from flask_restx import fields, Api, Resource, marshal
from flask_restx import reqparse
from sqlalchemy.exc import IntegrityError


class TodoDao(object):
    def __init__(self, todo_id, task):
        self.todo_id = todo_id
        self.task = task

        # This field will not be sent in the response
        self.status = 'active'


QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['ERROR_404_HELP'] = False
    setup_db(app)

    #   CORS Configuration
    # Allowing all origins to access api

    # setup flask-RESTX
    api = Api(app)

    category_ns = api.namespace('categories', description='Category operations')
    question_ns = api.namespace('questions', description='Question operations')
    quizzes_ns = api.namespace('quizzes', description='Quizzes operations')
    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    category_model = api.model('category_model', {
        '*': fields.Wildcard(fields.String)
    })
    category_list_model = api.model('category_list_model', {
        'questions': fields.List(fields.Nested(category_model)),
        'count': fields.Integer(readonly=True, description='Total number of questions available')
    })

    @question_ns.marshal_list_with(category_list_model)
    @category_ns.route('/')
    class CategoryList(Resource):
        '''Shows a list of all categories'''

        @category_ns.doc('list_categories')
        def get(self):
            '''List all categories'''
            categories = Category.query.all()
            catgs = {cat.id: cat.type for cat in categories}
            response = {
                "categories": catgs,
                "count": len(catgs)
            }
            return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    question_model = api.model('question', {
        'id': fields.Integer(readonly=True, description='The question unique identifier'),
        'question': fields.String(required=True, description='The question detail'),
        'answer': fields.String(required=True, description='The question answer'),
        'difficulty': fields.Integer(required=True, description='The question difficulty', default=1),
        'category': fields.Integer(required=True, description='The question category', default=1)
    })

    question_list_model = api.model('question_list', {
        'total_questions': fields.Integer(readonly=True, description='Total number of questions available'),
        'page': fields.Integer(required=False,
                               description=f'Page number. Each page contains {QUESTIONS_PER_PAGE} questions ',
                               default=1),
        'questions': fields.List(fields.Nested(question_model)),
        'categories': fields.Nested(category_model),
        "current_category": fields.Integer
    })

    @question_ns.route('/')
    class QuestionList(Resource):
        '''Shows a list of all questions'''

        def _page_index(self, page, array):
            '''Calculate pagination and validation against array
            :param page: page number
            :param array: data array
            :return: start_index, end_index of specified pagination
            '''
            start_index = (page - 1) * QUESTIONS_PER_PAGE
            end_index = start_index + QUESTIONS_PER_PAGE

            if page < 1:
                raise ValueError("Page is not a valid positive integer")

            if start_index > len(array) - 1:
                raise ValueError("Page is out of bound")

            if end_index > len(array):
                end_index = len(array)
            return start_index, end_index

        @question_ns.doc('list_questions')
        @question_ns.marshal_list_with(question_list_model)
        @question_ns.doc(params={'page': f'page number. Each page contains {QUESTIONS_PER_PAGE} questions'})
        def get(self):
            '''List all questions'''
            questions = Question.query.order_by(Question.id).all()
            # categories = Category.query.order_by(Category.id).all()
            categories = Category.query.get(1)
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, help='Page cannot be converted', default=1)
            args = parser.parse_args()
            page = args['page']
            print(args)
            start_index, end_index = self._page_index(page, questions)

            response = {
                "questions": questions[start_index:end_index],
                "total_questions": len(questions),
                "page": args['page'],
                "categories": None,
                "current_category": None
            }
            return response

        @question_ns.doc('post_question')
        @question_ns.marshal_with(question_model)
        @question_ns.expect(question_model)
        def post(self):
            '''Create a new question. Ensure that the difficulty and categories are a valid positive integer'''
            code = 201
            message = ""
            try:
                if api.payload["difficulty"] < 1 or api.payload["difficulty"] > 4:
                    message = "difficulty should be between 1 and 4"
                    code = 422
                else:
                    question = Question(**api.payload)
                    db.session.add(question)
                    db.session.commit()
                    api.payload["id"] = question.id
                    code = 201
            except IntegrityError:
                code = 422
                message = "The specified category is not valid"
                db.session.rollback()
            finally:
                db.session.close()
            if (code != 201):
                abort(code, message)
            return api.payload, 201

        @api.errorhandler(ValueError)
        def handle_custom_exception(error):
            '''Return a custom message and 422 status code'''
            return {'message': f'{error}'}, 422

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @question_ns.route('/<int:question_id>')
    class Questions(Resource):
        '''Shows a specific question'''

        @question_ns.doc('get_question')
        @question_ns.marshal_with(question_model)
        def get(self, question_id):
            '''Get questions by Id'''
            question = Question.query.get(question_id)
            if question == None:
                abort(404, f"question {question_id} does not exist.")

            return question

        @question_ns.doc('delete_question')
        def delete(self, question_id):
            '''Delete questions by Id'''
            try:
                question = Question.query.get(question_id)
                if question == None:
                    message = f"question {question_id} does not exist."
                    code = 404
                else:
                    db.session.delete(question)
                    db.session.commit()
                    code = 204
            except:
                code = 500
                message = f"Server encountered issue deleting question {question_id}"
                db.session.rollback()
            finally:
                db.session.close()

            if (code != 204):
                abort(code, message)
            return '', 204

    '''
     @TODO: 
     Create a POST endpoint to get questions based on a search term. 
     It should return any questions for whom the search term 
     is a substring of the question. 

     TEST: Search by any phrase. The questions list will update to include 
     only question that include that string within their question. 
     Try using the word "title" to start. 
     '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    search_model = api.model('search_model', {
        'searchTerm': fields.String(required=True, description="Search term")
    })
    search_result_model = api.model('search_result_model', {
        'count': fields.Integer(readonly=True, description='Number of questions found in the search'),
        'questions': fields.List(fields.Nested(question_model))
    })

    @question_ns.route('/search/')
    class QuestionSearch(Resource):
        '''Search for questions based on post body'''

        @question_ns.doc('search_questions')
        @question_ns.marshal_list_with(search_result_model)
        @question_ns.expect(search_model)
        def post(self):
            '''Search for question based on term all questions'''

            questions = Question.query.filter(Question.question.ilike(f"%{api.payload['searchTerm']}%")).all()

            response = {
                "questions": questions,
                "count": len(questions)
            }
            return response

    @question_ns.route('/filter')
    class QuestionFilter(Resource):
        '''Filter a question based on category'''

        @question_ns.doc('filter question by category')
        @question_ns.marshal_list_with(search_result_model)
        @question_ns.doc(params={'category': f'category unique identifier. You can get the list of categories by '
                                             f'making GET request to the category resource endpoint'})
        def get(self):
            '''List all questions'''
            parser = reqparse.RequestParser()
            parser.add_argument('category', type=int, default=1)
            args = parser.parse_args()
            category_id = args['category']
            questions = Question.query.filter(Question.category == category_id).all()

            response = {
                "questions": questions,
                "count": len(questions)
            }
            return response

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    quizz_category_model = api.model('quizz_category_model', {
        #'type': fields.String(required=True, description="Category description. "),
        'id': fields.Integer(required=True, description="Category id. 0 means all category")
    })
    quizz_model = api.model('quizz_model', {
        'quiz_category': fields.Nested(quizz_category_model, required=True),
        'previous_questions': fields.List(fields.Nested(question_model)),
    })
    quizz_response_model = api.model('quizz_response_model', {
        'question': fields.Nested(question_model, required=False, skip_none=True)
    })

    @quizzes_ns.route('/')
    class QuestionRandom(Resource):
        '''Get a random question based on category'''

        @quizzes_ns.expect(quizz_model)
        def post(self):
            '''get a random question'''
            category_id = api.payload['quiz_category']['id']

            if category_id != 0 and len(Category.query.filter(Category.id == category_id).all()) <= 0:
                abort(422, "Category is not valid")

            if category_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == category_id).all()

            bank = []
            for q in questions:
                if  q.id not in api.payload['previous_questions']:
                    bank.append(q.id)

            if len(bank) > 0:
                choice = random.choice(bank)
                question = Question.query.get(choice)
                response = {
                    'question': question
                }
                return marshal(response, quizz_response_model)
            return jsonify({
                'question': None
            })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    return app
