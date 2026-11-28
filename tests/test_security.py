import os
import unittest
from unittest.mock import patch

from gxb2.security import FixedWindowRateLimiter, normalized_origin, validate_production_config


class SecurityTests(unittest.TestCase):
    def test_rate_limiter(self):
        limiter=FixedWindowRateLimiter()
        self.assertEqual(limiter.allow("login","1.2.3.4",limit=2,window=60,now=100),(True,0))
        self.assertEqual(limiter.allow("login","1.2.3.4",limit=2,window=60,now=101),(True,0))
        allowed,retry=limiter.allow("login","1.2.3.4",limit=2,window=60,now=102)
        self.assertFalse(allowed); self.assertGreater(retry,0)
        self.assertEqual(limiter.allow("login","1.2.3.4",limit=2,window=60,now=161),(True,0))

    def test_normalized_origin(self):
        self.assertEqual(normalized_origin("https://game.example.com/"),"https://game.example.com")
        with self.assertRaises(ValueError): normalized_origin("game.example.com")

    def test_production_requires_https_admin_key_and_postgres(self):
        with patch.dict(os.environ,{"GXB3_PRODUCTION":"1"},clear=False):
            with self.assertRaises(RuntimeError):
                validate_production_config(http_host="0.0.0.0",public_origin="http://game.test",admin_key="x"*32,database_url="postgresql://db")
            with self.assertRaises(RuntimeError):
                validate_production_config(http_host="0.0.0.0",public_origin="https://game.test",admin_key="short",database_url="postgresql://db")
            with self.assertRaises(RuntimeError):
                validate_production_config(http_host="0.0.0.0",public_origin="https://game.test",admin_key="x"*32,database_url="")
            warnings=validate_production_config(http_host="0.0.0.0",public_origin="https://game.test",admin_key="x"*32,database_url="postgresql://db")
            self.assertEqual(warnings,[])


if __name__=="__main__":
    unittest.main()
