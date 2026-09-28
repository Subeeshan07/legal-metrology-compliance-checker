"""
Tests for Phase 9: Security and Production Hardening.
Verifies security headers, MIME / magic byte checks, rate limiting, and health endpoint.
"""

import io
import unittest
from app import app
from utils.file_utils import validate_image_signature, cleanup_expired_uploads
from utils.rate_limiter import RateLimiter


class TestSecurityHardening(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_security_headers_present(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_health_check_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "UP")
        self.assertIn("ocr_engine", data)
        self.assertIn("database", data)
        self.assertIn("timestamp", data)

    def test_magic_byte_signature_validator(self):
        # Valid PNG header
        valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        self.assertTrue(validate_image_signature(valid_png))

        # Valid JPEG header
        valid_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        self.assertTrue(validate_image_signature(valid_jpeg))

        # Disguised text / script
        fake_script = b"<?php echo 'malicious'; ?>"
        self.assertFalse(validate_image_signature(fake_script))

        fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
        self.assertFalse(validate_image_signature(fake_exe))

    def test_rate_limiter_logic(self):
        limiter = RateLimiter(max_requests=3, window_seconds=2)
        ip = "192.168.1.100"

        self.assertTrue(limiter.is_allowed(ip))
        self.assertTrue(limiter.is_allowed(ip))
        self.assertTrue(limiter.is_allowed(ip))
        # 4th request within window must be rejected
        self.assertFalse(limiter.is_allowed(ip))

    def test_invalid_image_upload_rejected(self):
        data = {
            "label_image": (io.BytesIO(b"Not a real image file!"), "fake.png")
        }
        response = self.client.post("/api/scan", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertIn("error", json_data)
        self.assertIn("Security validation failed", json_data["error"])

    def test_404_handler(self):
        response = self.client.get("/non-existent-endpoint-abc")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
