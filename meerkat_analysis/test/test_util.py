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
        mo.post("https://auth.emro.info/api/login",
               text="hei",
        )
        
        ld = util.LiveDownloader("http://test.test", username="test",
                                 password="password")
 
        mo.get("http://test.test/api/variables/all",
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
        mo.post("https://auth.emro.info/api/login",
                text="hei",
        )
        
        ld = util.LiveDownloader("http://test.test",
                                 password="password",
                                 username="test")
        mo.get("http://test.test/api/export/data/1",
               text="a1234aa")
        mo.get("http://test.test/api/export/get_status/1234",
               text=json.dumps({"status": 1, "success": 1}))
        mo.get("http://test.test/api/export/getcsv/1234",
               text="This is a test")
        filename = "test.test"
        ld.download_structured_data(filename)
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a test")
        os.remove(filename)
        
    @requests_mock.mock()
    def test_download_variables(self, mo):
        mo.post("https://auth.emro.info/api/login",
               text="hei",
        )
        
        ld = util.LiveDownloader("http://test.test",
                                 password="password",
                                 username="test")
        mo.get("http://test.test/api/variables/all",
               text="This is a test")
        filename = "test.test"
        ld.download_variables(filename)
        with open(filename, "r") as f:
            self.assertEqual(f.read(), "This is a test")
        os.remove(filename)

        
class LocationsTest(unittest.TestCase):
    """ Testing Locations class"""

    def setUp(self):
        with open("meerkat_analysis/test/test_data/locations.json") as f:
            self.locations = json.loads(f.read())
            
    def test_init(self):
        location = util.Locations(self.locations)
        self.assertEqual(location.locations, self.locations)

    def test_init_from_json_file(self):
        location = util.Locations.from_json_file(
            "meerkat_analysis/test/test_data/locations.json")
        self.assertEqual(location.locations, self.locations)

    @requests_mock.mock()
    def test_init_from_url(self, mo):

        mo.post("https://auth.emro.info/api/login",
               text="hei"
        )
        
        ld = util.LiveDownloader("http://test.test", username="test",
                                 password="password")
        mo.get("http://test.test/api/locations",
               text=json.dumps(self.locations))
        v = util.Locations.from_url(ld, "test.test")

        self.assertEqual(v.locations, self.locations)
        os.remove("test.test")
        
    def test_get_level(self):
        location = util.Locations(self.locations)

        clinics = location.get_level("clinic")
        self.assertEqual(sorted(clinics), sorted(["7", "8", "10", "11"]))
        
        clinics = location.get_level("clinic", only_case_report=False)
        self.assertEqual(sorted(clinics), sorted(["7", "8", "9", "10", "11"]))

        districts = location.get_level("district")
        self.assertEqual(sorted(districts), sorted(["4", "5", "6"]))

        regions = location.get_level("region")
        self.assertEqual(sorted(regions), sorted(["2", "3"]))

        regions = location.get_level("not_a_level")
        self.assertEqual(sorted(regions), [])
        
    def test_name(self):
        location = util.Locations(self.locations)
        self.assertEqual(location.name("7"), "Clinic 1")
        self.assertEqual(location.name(7), "Clinic 1")
        self.assertEqual(location.name("Not a location"), None)

    def test_population(self):
        location = util.Locations(self.locations)
        self.assertEqual(location.population("7"), 1500)
        self.assertEqual(location.population(7), 1500)
        self.assertEqual(location.population("Not a location"), 0)
