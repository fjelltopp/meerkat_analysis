from unittest import mock
import unittest
import requests_mock
import os
import json
import csv

from meerkat_analysis import util


class UtilTest(unittest.TestCase):
    """ Testing util"""

    @requests_mock.mock()
    def test_download_file(self, mo):
        mo.get("http://test.test", text="This is a test")
        filename = "test.test"
        util.download_file("http://test.test", filename)
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a test")

        os.remove(filename)
        mo.get("http://test.test?key=key", text="This is a second test")
        util.download_file("http://test.test",
                           filename,
                           params={"key": "key"})
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a second test")
        os.remove(filename)

    def test_load_from_json_file(self):
        v = {"test": {"test2": [1, 2, 3],
                      "test3": "test3"
                      },
             "test4": 1234
             }
        with open("test.test", "w") as f:
            f.write(json.dumps(v))
        new_v = util.load_from_json_file("test.test")
        self.assertEqual(v, new_v)
        os.remove("test.test")

class VariablesTest(unittest.TestCase):
    """ Testing the Variable class """
    def setUp(self):
        self.variables = {"id_1": {"name": "Test 1",
                                   "category": ["test1"],
                                   "id": "id_1"},
                          "id_2": {"name": "Test 2",
                                   "category": ["test1", "test2"],
                                   "id": "id_2"}

        }
    def test_init(self):
        """ Test various init methods """
        v = util.Variables(self.variables)
        self.assertEqual(v.variables, self.variables)
        self.assertEqual(sorted(v.groups["test1"]), ["id_1", "id_2"])
        self.assertEqual(sorted(v.groups["test2"]), ["id_2"])
                 
    def test_init_from_json_file(self):
        with open("test.test", "w") as f:
            f.write(json.dumps(self.variables))
        v = util.Variables.from_json_file("test.test")
        self.assertEqual(v.variables, self.variables)
        os.remove("test.test")
        
    @requests_mock.mock()
    def test_init_from_url(self, mo):
        ld = util.LiveDownloader("http://test.test", api_key="test")
        mo.get("http://test.test/api/variables/all?api_key=test",
               text=json.dumps(self.variables))
        v = util.Variables.from_url(ld, "test.test")

        self.assertEqual(v.variables, self.variables)
        os.remove("test.test")
        
    def test_init_from_csv(self):
        columns = ["id", "name", "category"]
        with open("test.test", "w") as f:
            out = csv.DictWriter(f, columns)
            out.writeheader()
            for variable in self.variables.values():
                new_variable = variable.copy()
                new_variable["category"] = ",".join(variable["category"])
                out.writerow(new_variable)
        v = util.Variables.from_csv_file("test.test")
        self.assertEqual(v.variables, self.variables)
        os.remove("test.test")

    def test_get_name(self):
        v = util.Variables(self.variables)
        self.assertEqual(v.name("id_1"), "Test 1")
    def test_get_id(self):
        v = util.Variables(self.variables)
        self.assertEqual(v.get_id("Test 1"), "id_1")
        self.assertEqual(v.get_id("Test 2"), "id_2")
        self.assertEqual(v.get_id("Does not exisit"), None)
        

class LiveDownloaderTest(unittest.TestCase):
    """ Test LiveDownloader class """
    @requests_mock.mock()
    def test_download_structured_data(self, mo):
        ld = util.LiveDownloader("http://test.test", api_key="test")
        mo.get("http://test.test/api/export/data?api_key=test",
               text="This is a test")
        filename = "test.test"
        ld.download_structured_data(filename)
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a test")
        os.remove(filename)
        
    @requests_mock.mock()
    def test_download_variables(self, mo):
        ld = util.LiveDownloader("http://test.test", api_key="test")
        mo.get("http://test.test/api/variables/all?api_key=test",
               text="This is a test")
        filename = "test.test"
        ld.download_variables(filename)
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a test")
        os.remove(filename)
