import json

import requests
from requests.auth import HTTPBasicAuth
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


class HttpReportService:
    def __init__(self, config):
        self.__status_code = 0
        self.__config = config
        self.__reports = []

    def get_reports_from_server(self):
        try:
            org_units_df = pd.read_csv(self.__config["org_units_file_name"])
            for each_endpoint in self.__config["endpoints"]:
                reports_df = pd.read_csv(each_endpoint["report_file_name"])
                print(reports_df.head())
                for index, each_report in reports_df.iterrows():
                    reports = []
                    locations_str = each_report.to_dict()["org_units"]
                    locations_list = locations_str.split(",")
                    for location in locations_list:
                        org_unit = org_units_df.loc[org_units_df["Org Unit"] == str(location)]["Org Unit Id"].iat[0]
                        org_unit_name = org_units_df.loc[org_units_df["Org Unit"] == str(location)]["Org Unit"].iat[0]
                        start_date = each_endpoint['default_start_date']
                        end_date = date.today()
                        url = each_endpoint["base"] + each_report["resource"]
                        data_set = each_report["data_set"]
                        frequency = each_report["frequency"]
                        program = each_report["program"]
                        if each_report["report_type"] == "aggregate":
                            params = {
                                "dataSet": data_set,
                                "orgUnit": org_unit,
                                'startDate': start_date,
                                'endDate': end_date,
                                'frequency': frequency
                            }
                        elif each_report["report_type"] == "tracker":
                            params = {
                                "program": program,
                                "orgUnit": org_unit,
                                'startDate': start_date,
                                'endDate': end_date,
                            }
                        else:
                            print("Missing Event resource")

                        print("Request for " + each_report[
                            "name"] + "for " + org_unit_name + " for the following parameters: " + str(params))
                        get_report = requests.get(url, params=params,
                                                  auth=HTTPBasicAuth(username=each_endpoint["username"],
                                                                     password=each_endpoint["password"]))
                        self.__status_code = get_report.status_code = get_report.status_code
                        if self.__status_code == 200:
                            print("Successful Request for " + each_report["name"] + "for " + org_unit_name)
                            report_json = json.loads(get_report.text)

                            if len(report_json) == 0:
                                print("Report is blank, please download it manually from server")
                            else:
                                if each_report["report_type"] == "aggregate":
                                    reports.append(report_json)
                                elif each_report["report_type"] == "tracker":
                                    data_elements_dict = []
                                    for facility_events in report_json["events"]:
                                        event_date = facility_events["eventDate"]
                                        org_unit = facility_events["orgUnit"]
                                        report_detail = facility_events["attributeOptionCombo"]
                                        event_datetime = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S.%f")
                                        e_period = event_datetime + relativedelta(months=1, day=1, days=-1)
                                        period = e_period.strftime("%Y%m")
                                        report_objs = list(facility_events["dataValues"])
                                        for report_obj in report_objs:
                                            report_obj["period"] = period
                                            report_obj["orgUnit"] = org_unit
                                            report_obj["report_detail"] = report_detail
                                            data_elements_dict.append(report_obj)
                                    facility_report = {"dataValues": data_elements_dict}
                                    reports.append(facility_report)
                                else:
                                    print("Unsupported output")
                        else:
                            print("Request not successful for " + each_report["name"] + "for " + org_unit_name)
                    if len(reports) > 0:
                        self.__reports.append(reports)
        except Exception as e:
            self.__status_code = 500
            print(f"Error in processing request:{e}")

    def get_reports(self):
        return self.__status_code, self.__reports

    def get_data(self, resource, page_size):
        response = []
        try:
            for each_endpoint in self.__config["endpoints"]:
                url = each_endpoint["base"] + "/" + resource
                params = {
                    "pageSize": page_size,
                }
                get_report = requests.get(url, params=params,
                                          auth=HTTPBasicAuth(username=each_endpoint["username"],
                                                             password=each_endpoint["password"]))
                self.__status_code = get_report.status_code = get_report.status_code
                if self.__status_code == 200:
                    print(f"Successful Request for {resource}")
                    response = json.loads(get_report.text)
                    return self.__status_code, response
                else:
                    return self.__status_code, response
        except Exception as e:
            self.__status_code = 500
            response.append(e)
            return self.__status_code, response
