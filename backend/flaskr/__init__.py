import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy.sql.expression import func
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    # Returns upto 10 questions per page
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={r"/api/*": {"origins": '*'}})

    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # @app.route('/')
    # def index():
    #     return 'Welcome to the Udacitrivia API'




  # @TODO:
  # Create an endpoint to handle GET requests
  # for all available categories.

    @app.route('/categories')
    def get_categories():
        # API endpoint gets all categories in the DB.
        # query the DB for all categories
        categories = Category.query.all()
        # format categories
        formated_categories = [category.format() for category in categories]

        # return in JSON w/success and formated list
        return jsonify({
            'success': True,
            'categories': formated_categories
        })

  #   '''
  # @TODO:
  # Create an endpoint to handle GET requests for questions,
  # including pagination (every 10 questions).
  # This endpoint should return a list of questions,
  # number of total questions, current category, categories.

  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions.
  # '''
    @app.route('/questions')
    def retrieve_questions():
        # API endpoint retrieves all questions.
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })
  #   '''
  # @TODO:
  # Create an endpoint to DELETE question using a question ID.

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page.
  # '''
    @app.route('/questions/<int:questions_id>', methods=['DELETE'])
    def delete_question(questions_id):
        try:
            question = Question.query.filter(Question.id == questions_id).one_or_none()
            print("delete_question 2")
            if question is None:
                abort(404)
            question.delete()
            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, all_questions)

            return jsonify({
                'success': True,
                'deleted': questions_id,
                'questions': current_questions,
                'total_questions': len(all_questions)
            })
        except Exception as e:
            print(e)
            abort(422)

  #   '''
  # @TODO:
  # Create an endpoint to POST a new question,
  # which will require the question and answer text,
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab,
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.
  # '''
    @app.route('/questions', methods=["POST"])
    def create_question():
        # API endpoint creates a new question in database
        try:
            body = request.get_json()

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_question_category = body.get('category', None)
            new_question_difficulty = body.get('difficulty', None)

            question = Question(question=new_question, answer=new_answer,
                                category=new_question_category, difficulty=new_question_difficulty)
            question.insert()
            return jsonify({
                "success": True
            })
        except:
            abort(404)
  #   '''
  # @TODO:
  # Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term
  # is a substring of the question.

  # TEST: Search by any phrase. The questions list will update to include
  # only question that include that string within their question.
  # Try using the word "title" to start.
  # '''

    @app.route('/search/questions', methods=["POST"])
    def search_question():
        # API endpoint searches database questions by term

        try:
            content = request.get_json()

            searchTerm = content.get('searchTerm', '')

            if (searchTerm is None or searchTerm == ''):
                abort(400)

            search = "%{}%".format(searchTerm)

            questions = Question.query.all()

            questions_found = Question.query.filter(
                Question.question.ilike(search))

            questions_found_format = [question.format()
                                      for question in questions_found]

            return jsonify({
                "success": True,
                "total_questions": len(questions),
                "questions": questions_found_format,
                "current_category": None
            })
        except:
            abort(400)
  #   '''
  # @TODO:
  # Create a GET endpoint to get questions based on category.

  # TEST: In the "List" tab / main screen, clicking on one of the
  # categories in the left column will cause only questions of that
  # category to be shown.
  # '''
    @app.route('/categories/<category_id>/questions')
    def list_by_category(category_id):
        # API endpoint returns questions by category


        try:
            questions = Question.query.filter_by(
                category=str(category_id)).all()
            formatted_questions = [question.format() for question in questions]
            total_questions = len(formatted_questions)
            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": total_questions,
            })

        except:
            abort(400)

#     '''
#   @TODO:
#   Create a POST endpoint to get questions to play the quiz.
#   This endpoint should take category and previous question parameters
#   and return a random questions within the given category,
#   if provided, and that is not one of the previous questions.

#   TEST: In the "Play" tab, after a user selects "All" or a category,
#   one question at a time is displayed, the user is allowed to answer
#   and shown whether they were correct or not.
#   ''' - Done
#####


    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        # API endpoint returns random question to play quiz.

        # get data and values
        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        quiz_category = data.get('quiz_category', None)

        # return 400 if error
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)

        if (quiz_category['id']):
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()
        else:
            # questions by category
            questions = Question.query.all()


        # create a method to get a random question
        def randomize_questions():
            return questions[random.randint(0, len(questions)-1)]

        # randomize next question
        next_question = randomize_questions()

        # make sure question has not been called yet.
        found = True

        while found:
            if next_question.id in previous_questions:
                next_question = get_random_question()
            else:
                found = False

        return jsonify({
            'success': True,
            'question': next_question.format(),
        }), 200



#     '''
#   @TODO:
#   Create error handlers for all expected errors
#   including 404 and 422. - Done
#   '''
    # Bad request error (400)

    @app.errorhandler(400)
    def bad_request(error):
        # Bad request error handler
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'There is a bad request error.'
        }), 400

    # Resource not found (404)
    @app.errorhandler(404)
    def not_found(error):
        '''Resource not found error handler.'''
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource can not found.'
        }), 404

    # Unprocesable entity (422)
    @app.errorhandler(422)
    def unprocessable_entity(error):
        '''Unprocessable entity error handler'''
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity. Item could not be deleted.'
        }), 422

    # Internal server error (500)
    @app.errorhandler(500)
    def internal_server_error(error):
        '''Internal service error handler'''
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'There is an internal service error. Please try again.'
        }), 500

    return app
