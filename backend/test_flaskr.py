import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_invalid_url(self):
        response = self.client().get('/invalid', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    """
    Categories end point
    """

    def test_get_categories_success(self):
        response = self.client().get('/categories', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data) > 0, True)

    """
    /questions GET end point
    """

    def test_get_questions_success(self):
        response = self.client().get('/questions', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']), 10)  # Should return 10 item per page

    def test_get_questions_success_with_parameter1(self):
        response = self.client().get('/questions?page=1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']), 10)  # Should return 10 item per page

    def test_get_questions_success_with_parameter2(self):
        response = self.client().get('/questions?page=2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) > 1, True)

    def test_get_questions_invalid1(self):
        response = self.client().get('/questions?page=100', follow_redirects=True)
        self.assertEqual(response.status_code, 422)

    def test_get_questions_invalid2(self):
        response = self.client().get('/questions?page=-100', follow_redirects=True)
        self.assertEqual(response.status_code, 422)

    def test_get_questions_invalid3(self):
        response = self.client().get('/questions?page=dsadasdsadasdas', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    """
    /questions POST end point
    """

    def test_post_questions_success(self):
        data = {
            "question": "Did we land on the moon?",
            "answer": "No",
            "difficulty": 1,
            "category": 1
        }
        response = self.client().post('/questions', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 201)

    def test_post_questions_failure_invalid(self):
        response = self.client().post('/questions', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_post_questions_failure_invalid_value1(self):
        data = {
            "question": "Did we land on the moon?",
            "answer": "No",
            "difficulty": 1,
            "category": -1
        }
        response = self.client().post('/questions', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 422)

    def test_post_questions_failure_invalid_value2(self):
        data = {
            "question": "Did we land on the moon?",
            "answer": "No",
            "difficulty": 10,
            "category": 1
        }
        response = self.client().post('/questions', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 422)

    """
    /questions/filter GET end point
    """

    def test_get_questions_filter_success(self):
        response = self.client().get('/questions/filter', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) > 1, True)
        self.assertEqual(data['questions'][0]['category'], 1)

    def test_get_questions_filter_success_with_parameter1(self):
        response = self.client().get('/questions/filter?category=1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) > 1, True)
        self.assertEqual(data['questions'][0]['category'], 1)

    def test_get_questions_filter_success_with_parameter2(self):
        response = self.client().get('/questions/filter?category=3', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) > 1, True)
        self.assertEqual(data['questions'][0]['category'], 3)

    def test_get_questions_filter_invalid1(self):
        response = self.client().get('/questions/filter?category=10', follow_redirects=True)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) == 0, True)

    def test_get_questions_filter_invalid2(self):
        response = self.client().get('/questions/filter?category=-1', follow_redirects=True)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']) == 0, True)

    def test_get_questions_filter_invalid3(self):
        response = self.client().get('/questions/filter?category=dsadsadasdas', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    """
    / questions / search /  POST End point
    """

    def test_post_questions_search_success(self):
        data = {
            "searchTerm": "What"
        }
        response = self.client().post('/questions/search', json=data, follow_redirects=True)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['questions']) > 0, True)

    def test_post_questions_search_fail(self):
        response = self.client().post('/questions/search', follow_redirects=True)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)

        """
       / questions / {question_id} /  GET  specific question
       """

    def test_get_questions_by_id_successl(self):
        response = self.client().get('/questions/2', follow_redirects=True)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'] == 2, True)

    def test_get_questions_by_id_fail1(self):
        response = self.client().get('/questions/10000', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_get_questions_by_id_fail2(self):
        response = self.client().get('/questions/adsada', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    """
       / questions / {question_id} /  DELETE  specific question
    """

    def test_delete_questions_by_id_successl(self):
        # Test by posting a question then delete it
        data = {
            "question": "Did we land on the moon?",
            "answer": "No",
            "difficulty": 1,
            "category": 1
        }
        # Create
        response = self.client().post('/questions', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        # Delete
        del_response = self.client().delete(f'/questions/{data["id"]}', follow_redirects=True)
        self.assertEqual(del_response.status_code, 204)

        # Check
        check_response = self.client().get(f'/questions/{data["id"]}', follow_redirects=True)
        self.assertEqual(check_response.status_code, 404)

    def test_delete_questions_by_id_failure1(self):
        # Test by posting a question then delete it
        data = {
            "question": "Did we land on the moon?",
            "answer": "No",
            "difficulty": 1,
            "category": 1
        }
        # Create
        response = self.client().post('/questions', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        # Delete
        del_response = self.client().delete(f'/questions/{data["id"]}', follow_redirects=True)
        self.assertEqual(del_response.status_code, 204)

        # Delete
        del_response = self.client().delete(f'/questions/{data["id"]}', follow_redirects=True)
        self.assertEqual(del_response.status_code, 404)

        # Check
        check_response = self.client().get(f'/questions/{data["id"]}', follow_redirects=True)
        self.assertEqual(check_response.status_code, 404)

    def test_delete_questions_by_id_failure2(self):
        # Test by posting a question then delete it
        del_response = self.client().delete(f'/questions/dsadasdasdsa', follow_redirects=True)
        self.assertEqual(del_response.status_code, 404)

    """
    /quizzes END point POST
    """

    def test_post_quiz_success(self):
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": [
                {
                    "question": "Did we land on the moon",
                    "answer": "No",
                    "difficulty": 1,
                    "category": 1
                }
            ]
        }
        response = self.client().post('/quizzes', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["question"]["category"], 1)

    def test_post_quiz_failure(self):
        data = {
            "quiz_category": {
                "id": 1000
            },
            "previous_questions": [
                {
                    "question": "Did we land on the moon",
                    "answer": "No",
                    "difficulty": 1,
                    "category": 1
                }
            ]
        }
        response = self.client().post('/quizzes', json=data, follow_redirects=True)
        self.assertEqual(response.status_code, 422)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
