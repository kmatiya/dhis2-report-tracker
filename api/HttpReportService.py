import json

import requests
from requests.auth import HTTPBasicAuth
from datetime import date


class HttpReportService:
    def __init__(self, config):
        self.__config = config
        self.__reports = []

    def get_location_for_all_endpoints(self):
        locations = []
        for each_endpoint in self.__config["endpoints"]:
            for each_location in each_endpoint["org_units"]:
                locations.append({
                    "id": each_location['id'],
                    "name": each_location['name']
                })
        locations = locations
        return locations

    def get_location_endpoint(self, location):
        for each_endpoint in self.__config["endpoints"]:
            for each_location in each_endpoint["org_units"]:
                if location == each_location['id']:
                    return each_endpoint

    def get_reports_from_server(self):
        locations = self.get_location_for_all_endpoints()
        for each_report in self.__config["reports"]:
            reports = []
            for location in locations:
                location_end_point = self.get_location_endpoint(location['id'])
                start_date = location_end_point['default_start_date']
                end_date = date.today()
                url = location_end_point["base"] + each_report["resource"]
                data_set = each_report["dataSet"]
                params = {
                    "dataSet": data_set,
                    "orgUnit": location['id'],
                    'startDate': start_date,
                    'endDate': end_date
                }

                print("Request for " + each_report["name"] + " for the following parameters: " + str(params))
                get_report = requests.get(url, params=params,
                                          auth=HTTPBasicAuth(username=location_end_point["username"],
                                                             password=location_end_point["password"]))
                if get_report.status_code == 200:
                    print("Successful Request for " + each_report["name"])
                    report_json = json.loads(get_report.text)

                    for e in report_json['dataValues']:
                        e["dataSet"] = data_set
                        e['startDate'] = start_date
                        e['endDate'] = end_date
                    if len(report_json) == 0:
                        print("Report is blank, please download it manually from server")
                    else:
                        reports.append(report_json)
            if len(reports) > 0:
                self.__reports.append(reports)

    def get_reports(self):
        return self.__reports
