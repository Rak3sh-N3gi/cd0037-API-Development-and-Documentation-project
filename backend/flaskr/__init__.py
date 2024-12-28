from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question = [question.format() for question in selection]
    current_questions = question[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        CategoryData = Category.query.order_by(Category.id).all()
        categories = {}
        for x in CategoryData:
            categories[x.id] = x.type
        return jsonify(
            {
                "categories": categories
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        
        if len(current_questions) == 0:
            abort(404)

        CategoryData = Category.query.order_by(Category.id).all()
        categories = {}
        for x in CategoryData:
            categories[x.id] = x.type

        return jsonify(
            {
                # "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                # "categories": Category.query.all(),
                "categories": categories,
                "current_category": 1
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)

        question.delete()
        return jsonify(
            {
                "success": True,
                "deleted": question_id
            }
        )
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions/add", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_difficulty = body.get("difficulty", None)
        new_category = body.get("category", None)

        if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
            abort(422)

        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
        question.insert()

        return jsonify(
            {
                "success": True,
                "created": question.id
            }
        )
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        if search_term is None:
            abort(422)

        selection = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                # "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all())
            })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questionsBasedOnCategories(category_id):
        selection = Question.query.filter(Question.category==category_id).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                # "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category": category_id
            }
        )
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        if quiz_category is None:
            abort(422)

        if quiz_category["id"] == 0:
            selection = Question.query.all()
        else:
            selection = Question.query.filter(Question.category==quiz_category["id"]).all()

        if len(previous_questions) >= len(selection):
            return jsonify(
                {
                    "question": None
                }
            )

        question = random.choice(selection)
        while question.id in previous_questions:
            question = random.choice(selection)

        return jsonify(
            {
                "question": question.format()
            }
        )
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable entity"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({"success": False, "error": 400, "message": "bad request"}), 
        400,
    )

    @app.errorhandler(500)
    def server_error(error):
        return (jsonify({"success": False, "error": 500, "message": "Server error"}), 
        400,
    )
    return app

