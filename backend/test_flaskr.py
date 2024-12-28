import os
import unittest

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "abc"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            # db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["categories"])

    def test_retrieve_questions(self):
        response = self.client.get("/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])

    def test_delete_question(self):
        with self.app.app_context():
            question = Question(
                question="Test Question",
                answer="Test Answer",
                category=1,
                difficulty=1
            )
            question.insert()

            response = self.client.delete(f"/questions/{question.id}")
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertTrue(data["success"])
            self.assertEqual(data["deleted"], question.id)

    def test_delete_question_not_found(self):
        response = self.client.delete("/questions/999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_create_question(self):
        response = self.client.post("/questions/add", json={
            "question": "Test Question",
            "answer": "Test Answer",
            "category": 1,
            "difficulty": 1
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

    def test_create_question_missing_data(self):
        response = self.client.post("/questions/add", json={})
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])

    def test_create_question_invalid_data(self):
        response = self.client.post("/questions/add", json={
            "question": "Test Question",
            "answer": "Test Answer",
            "category": 1
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])

    def test_search_questions(self):
        response = self.client.post("/questions", json={"searchTerm": "What"})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_search_questions_missing_data(self):
        response = self.client.post("/questions", json={"searchTerm": None})
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])

    def test_retrieve_questions_by_category(self):
        response = self.client.get("/categories/1/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])

    def test_retrieve_questions_by_category_not_found(self):
        response = self.client.get("/categories/999/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])

    def test_retrieve_quiz_question(self):
        response = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {"type": "Science", "id": 1}
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["question"])

    def test_retrieve_quiz_question_no_category(self):
        response = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": None
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["message"], "Unprocessable entity")

    def test_retrieve_quiz_question_no_more_questions(self):
        response = self.client.post("/quizzes", json={
            "previous_questions": [ 2, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
            "quiz_category": {"type": "Science", "id": 1}
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(data["question"])

    def test_error_404(self):
        response = self.client.get("/invalid")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 404)
        self.assertEqual(data["message"], "Resource not found")

    def test_error_422(self):
        response = self.client.post("/questions/add", json={})
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 422)
        self.assertEqual(data["message"], "Unprocessable entity")
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
