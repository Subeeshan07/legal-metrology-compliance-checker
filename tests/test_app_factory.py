"""
Tests for create_app() application factory.
"""

import unittest
from flask import Flask
from app import create_app
from config.settings import Config


class TestAppFactory(unittest.TestCase):

    def test_create_app_returns_flask_instance(self):
        test_app = create_app()
        self.assertIsInstance(test_app, Flask)

    def test_create_app_with_custom_dict_config(self):
        custom_config = {
            "TESTING": True,
            "CUSTOM_FLAG": "ACTIVE",
        }
        test_app = create_app(custom_config)
        self.assertTrue(test_app.config["TESTING"])
        self.assertEqual(test_app.config["CUSTOM_FLAG"], "ACTIVE")

    def test_blueprints_are_registered(self):
        test_app = create_app()
        blueprint_names = test_app.blueprints.keys()
        self.assertIn("web", blueprint_names)
        self.assertIn("scan", blueprint_names)
        self.assertIn("product", blueprint_names)
        self.assertIn("analytics", blueprint_names)
        self.assertIn("rules", blueprint_names)


if __name__ == "__main__":
    unittest.main()
