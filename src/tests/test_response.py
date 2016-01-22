import subprocess
import os
import unittest
import filecmp


class Test(unittest.TestCase):

    def setUp(self):
        self.expected_file = 'tests/fixtures/expected_response.json'
        self.temporary_test_file = 'tests/fixtures/result.json'

    def test_py2swagger_output(self):
        with open(self.temporary_test_file, 'a+b') as result:
            p = subprocess.Popen(['py2swagger', 'drf2swagger', 'testapp.settings'],
                                 stdout=result, stderr=subprocess.PIPE, cwd='tests/')
            p.communicate()
        self.assertTrue(filecmp.cmp(self.expected_file, self.temporary_test_file))

    def tearDown(self):
        if os.path.exists(self.temporary_test_file):
            os.remove(self.temporary_test_file)
