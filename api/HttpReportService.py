import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


class HttpReportService:
    def __init__(self, config, max_workers=10):
        self.__status_code = 0
        self.__config = config
        self.__reports = []
        self.max_workers = max_workers

    def get_reports_from_server(self, organization_units_df):
        try:
            # Fast org unit lookup (same result as old .loc[…].iat[0])
            org_unit_map = dict(
                zip(organization_units_df["name"], organization_units_df["id"])
            )

            for each_endpoint in self.__config["endpoints"]:
                reports_df = pd.read_csv(each_endpoint["report_file_name"])
                print(reports_df.head())

                session = requests.Session()
                session.auth = HTTPBasicAuth(
                    username=each_endpoint["username"],
                    password=each_endpoint["password"]
                )
                session.headers.update({"Accept": "application/json"})

                for _, each_report in reports_df.iterrows():
                    reports = []

                    locations_list = str(each_report["org_units"]).split(",")

                    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = []

                        for location in locations_list:
                            location = location.strip()
                            org_unit = org_unit_map.get(location)

                            if not org_unit:
                                print(f"Org unit {location} not found")
                                continue

                            start_date = each_endpoint["default_start_date"]
                            end_date = date.today()
                            url = each_endpoint["base"] + each_report["resource"]

                            if each_report["report_type"] == "aggregate":
                                params = {
                                    "dataSet": each_report["data_set"],
                                    "orgUnit": org_unit,
                                    "startDate": start_date,
                                    "endDate": end_date,
                                    "frequency": each_report["frequency"],
                                }
                            elif each_report["report_type"] == "tracker":
                                params = {
                                    "program": each_report["program"],
                                    "orgUnit": org_unit,
                                    "startDate": start_date,
                                    "endDate": end_date,
                                }
                            else:
                                print("Missing Event resource")
                                continue

                            print(
                                f"Request for {each_report['name']} "
                                f"for {location} with parameters: {params}"
                            )

                            futures.append(
                                executor.submit(
                                    self.__fetch_and_format_report,
                                    session,
                                    url,
                                    params,
                                    each_report["name"],
                                    location,
                                    each_report["report_type"]
                                )
                            )

                        for future in as_completed(futures):
                            result = future.result()
                            if result:
                                reports.append(result)

                    if len(reports) > 0:
                        self.__reports.append(reports)

        except Exception as e:
            self.__status_code = 500
            print(f"Error in processing request: {e}")

    def __fetch_and_format_report(
        self, session, url, params, report_name, location, report_type
    ):
        try:
            response = session.get(url, params=params)
            self.__status_code = response.status_code

            if response.status_code != 200:
                print(f"Request not successful for {report_name} for {location}")
                return None

            print(f"Successful Request for {report_name} for {location}")
            report_json = response.json()

            if not report_json:
                print("Report is blank, please download it manually from server")
                return None

            if report_type == "aggregate":
                return report_json

            if report_type == "tracker":
                data_elements_dict = []

                for event in report_json.get("events", []):
                    event_date = event["eventDate"]
                    org_unit = event["orgUnit"]
                    report_detail = event.get("attributeOptionCombo")

                    event_datetime = datetime.strptime(
                        event_date, "%Y-%m-%dT%H:%M:%S.%f"
                    )
                    e_period = event_datetime + relativedelta(
                        months=1, day=1, days=-1
                    )
                    period = e_period.strftime("%Y%m")

                    for report_obj in event.get("dataValues", []):
                        report_obj["period"] = period
                        report_obj["orgUnit"] = org_unit
                        report_obj["report_detail"] = report_detail
                        data_elements_dict.append(report_obj)

                return {"dataValues": data_elements_dict}

            print("Unsupported output")
            return None

        except Exception as e:
            print(f"Error fetching report {report_name} for {location}: {e}")
            return None

    def get_reports(self):
        return self.__status_code, self.__reports

    def get_data(self, resource, page_size):
        response = []
        try:
            for each_endpoint in self.__config["endpoints"]:
                session = requests.Session()
                session.auth = HTTPBasicAuth(
                    username=each_endpoint["username"],
                    password=each_endpoint["password"]
                )
                session.headers.update({"Accept": "application/json"})

                url = each_endpoint["base"].rstrip("/") + "/" + resource
                params = {"pageSize": page_size}

                r = session.get(url, params=params)
                self.__status_code = r.status_code

                if r.status_code == 200:
                    print(f"Successful Request for {resource}")
                    response = r.json()
                    return self.__status_code, response
                else:
                    print(f"Failed to get {resource}")
                    return self.__status_code, response

        except Exception as e:
            self.__status_code = 500
            response.append(e)
            return self.__status_code, response
