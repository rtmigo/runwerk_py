# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT


import os
import sys
import unittest
import warnings
from pathlib import Path
import requests
from runwerk import RunWerk

server_file_py = Path(__file__).parent / 'server.py'
command = [str(server_file_py)]


class TestFlaskBg(unittest.TestCase):

    def assert_not_running(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            requests.get('http://127.0.0.1:5000/say-hi')

    def assert_running(self):
        self.assertEqual(requests.get('http://127.0.0.1:5000/say-hi').text,
                         'privet')

    def test_command_interpreter_exe(self):
        self.assert_not_running()
        # we do not need to specify `command=`
        with RunWerk([sys.executable, str(server_file_py)]):
            self.assert_running()
        self.assert_not_running()

    def test_command_interpeter_none(self):
        self.assert_not_running()
        with RunWerk([None, str(server_file_py)]):
            self.assert_running()
        self.assert_not_running()

    def test_module(self):
        with RunWerk(module="tests.server"):
            self.assert_running()
        self.assert_not_running()

    def test_start_stop(self):
        # test the server is not running (yet)
        with self.assertRaises(requests.exceptions.ConnectionError):
            requests.get('http://127.0.0.1:5000/say-hi')

        # run server and get two different responses
        with RunWerk(command=command):
            self.assertEqual(requests.get('http://127.0.0.1:5000/say-hi').text,
                             'privet')
            self.assertEqual(requests.get('http://127.0.0.1:5000/say-bye').text,
                             'poka')

        # test the server is stopped
        with self.assertRaises(requests.exceptions.ConnectionError):
            requests.get('http://127.0.0.1:5000/say-hi')

    def test_env(self):
        assert os.environ.get('my_test_x_variable') is None

        with RunWerk(command):
            self.assertEqual(requests.get('http://127.0.0.1:5000/get-x').text,
                             '')

        with RunWerk(command, add_env={'my_test_x_variable': '42'}):
            self.assertEqual(requests.get('http://127.0.0.1:5000/get-x').text,
                             '42')

        # we did not change the environment: the variable was passed to
        # particular Flask instance, so if we start again, the variable is
        # not defined
        with RunWerk(command):
            self.assertEqual(requests.get('http://127.0.0.1:5000/get-x').text,
                             '')

    def test_env_flaskrun_default(self):
        del os.environ['RUNWERK_ENABLED']
        self.assert_not_running()
        with RunWerk(command):
            self.assert_running()

    def test_env_flaskrun_1(self):
        os.environ['RUNWERK_ENABLED'] = '1'
        self.assert_not_running()
        with RunWerk(command):
            self.assert_running()

    def test_env_flaskrun_true(self):
        os.environ['RUNWERK_ENABLED'] = 'true'
        self.assert_not_running()
        with RunWerk(command):
            self.assert_running()

    def test_env_flaskrun_0(self):
        os.environ['RUNWERK_ENABLED'] = ' 0 '  # intentional spaces
        self.assert_not_running()
        with RunWerk(command):
            self.assert_not_running()

    def test_env_flaskrun_false(self):
        os.environ['RUNWERK_ENABLED'] = 'fAlSe'
        self.assert_not_running()
        with RunWerk(command):
            self.assert_not_running()

    def test_env_flaskrun_labuda(self):
        os.environ['RUNWERK_ENABLED'] = 'labuda'
        self.assert_not_running()

        with self.assertWarns(Warning):
            with RunWerk(command):
                self.assert_running()



if __name__ == "__main__":
    TestFlaskBg().test_env()
