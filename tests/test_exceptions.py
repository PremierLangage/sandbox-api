# test_exceptions.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>


import http
import unittest

import sandbox_api



class Dummy:
    pass



class MyTestCase(unittest.TestCase):
    
    def test_sandbox_status(self):
        for status in (s for s in map(int, http.HTTPStatus) if s >= 300):
            self.assertTrue(hasattr(sandbox_api, "Sandbox" + str(status)))
    
    
    def test_status_exceptions(self):
        a = Dummy()
        a.status_code = 404
        self.assertIsInstance(sandbox_api.status_exceptions(a), sandbox_api.Sandbox404)



if __name__ == '__main__':
    unittest.main()
