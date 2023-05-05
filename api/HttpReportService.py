import json

import requests
from requests.auth import HTTPBasicAuth
from datetime import date
import pandas as pd


class HttpReportService:
    def __init__(self, config):
        self.__config = config
        self.__reports = []

    def get_reports_from_server(self):
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        for each_endpoint in self.__config["endpoints"]:
            reports_df = pd.read_csv(each_endpoint["report_file_name"])
            print(reports_df.head())
            for index, each_report in reports_df.iterrows():
                reports = []
                locations = reports_df["org_units"].tolist()[0].split(",")
                for location in locations:
                    org_unit = org_units_df.loc[org_units_df["Org Unit"] == str(location)]["Org Unit Id"].iat[0]
                    org_unit_name = org_units_df.loc[org_units_df["Org Unit"] == str(location)]["Org Unit"].iat[0]
                    start_date = each_endpoint['default_start_date']
                    end_date = date.today()
                    url = each_endpoint["base"] + each_report["resource"]
                    data_set = each_report["data_set"]
                    params = {
                        "dataSet": data_set,
                        "orgUnit": org_unit,
                        'startDate': start_date,
                        'endDate': end_date
                    }

                    print("Request for " + each_report[
                        "name"] + "for " + org_unit_name + " for the following parameters: " + str(params))
                    get_report = requests.get(url, params=params,
                                              auth=HTTPBasicAuth(username=each_endpoint["username"],
                                                                 password=each_endpoint["password"]))
                    if get_report.status_code == 200:
                        print("Successful Request for " + each_report["name"] + "for " + org_unit_name)
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
