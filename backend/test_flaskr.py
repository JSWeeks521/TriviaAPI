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
        self.database_path = "postgresql://postgres:Postgres@{}/{}".format(
            'localhost:5432', self.database_name)
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

    def test_get_categories(self):
        '''Test for get_categories'''

        # make a request and get response data
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # assert the response data: success=true, response code, categories and length
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_retrieve_questions(self):
        '''Test retrieve_questions'''

        # run a query to get total question count
        questions = Question.query.count()

        # make a request and get response data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # assert response data: success, status code, questions, total_questions, categories, current_category
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        # total_questions should be equal to 'questions'
        self.assertEqual(questions, data['total_questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(6, data['current_category'])

    def test_delete_questions(self):
        '''Test delete_question by id'''

        # make a request and get data
        response = self.client().delete('/questions/6')
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(response.status_code, 422)

    def test_create_question(self):
        '''Test create_question'''

        # make a request and get data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # test for success
        self.assertEqual(data['success'], True)

    def test_search_questions(self):
        '''Test search_questions'''

        # make a request and get data. Include a searchTerm that won't be found. use client.post
        response = self.client().post('/search/questions',
                                      json={'searchTerm': 'abc'})
        data = json.loads(response.data)

        # test for success, length of total_questions, questions and current category
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)

        # make sure length of questions found = 0
        self.assertEqual(len(data['questions']), 0)

        self.assertTrue(6, data['current_category'])

    def test_list_by_category(self):
        '''Test list_by_category. Should search by ID'''

        # make a request and get data by ID
        response = self.client().get('categories/2/questions')
        data = json.loads(response.data)

        # test for success, questions, total questions
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        # 4 questions in category 2 as of now
        self.assertEqual(4, data['total_questions'])
        # questions should not be equal to 0
        self.assertNotEqual(len(data['questions']), 0)

    def test_play_quiz(self):
        '''Test play_quiz
            To test this properly, you must run a client().post into the response
        '''
        test_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'Sports',
                'id': 6
            }
        }
        # make a request and get the data
        response = self.client().post('/quizzes', json=test_data)
        data = json.loads(response.data)

        # test for success, question and response
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
