import pandas as pd
from datetime import datetime, timedelta
from datetime import date
import os
import os.path


class ReportGenerator:
    def __init__(self, reports, config):
        self.__reports = reports
        self.__config = config

    def get_dhis2_period(self, start_date, end_date, frequency: str):
        periods = ""
        if frequency.strip().lower() == "monthly":
            periods = pd.date_range(start_date, end_date, freq="M").to_list()
        if frequency.strip().lower() == "quarterly":
            periods = pd.date_range(start_date, end_date, freq="Q").to_list()
        return periods

    def format_dhis2_date(self, date_of_report, frequency):
        split_date = str(date_of_report).split("-")
        period = ""
        if frequency.strip().lower() == "monthly":
            period = split_date[0] + split_date[1]
        if frequency.strip().lower() == "quarterly":
            day = int(split_date[2].split(" ")[0])
            timestamp = pd.Timestamp(int(split_date[0]), int(split_date[1]), day)
            period = split_date[0] + "Q" + str(timestamp.quarter)
        return period

    def get_data_frame(self):
        mode_of_generation = self.__config["report_generation"]
        if mode_of_generation == "tracker":
            report_file = self.__config["tracker_file_name"]
            file_name = report_file + '.xlsx'
            writer = pd.ExcelWriter(file_name,
                                    engine='xlsxwriter',
                                    engine_kwargs={'options': {'strings_to_numbers': True}})
            report_dict = []

        else:
            report_file = self.__config["full_report_file_name"]

        base_location = self.__config["base_file_path"]
        data_elements_df = pd.read_csv(self.__config["data_elements_file_name"])
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        category_option_combinations_df = pd.read_csv(self.__config["category_option_combinations"])
        report_due_day = self.__config["report_due_day"]
        print("Create files for each report")

        for each_endpoint in self.__config["endpoints"]:
            report_config_df = pd.read_csv(each_endpoint["report_file_name"])
            if mode_of_generation != "tracker":
                report_file = self.__config["full_report_file_name"]
                file_name = report_file + '.xlsx'
                writer = pd.ExcelWriter(file_name,
                                        engine='xlsxwriter',
                                        engine_kwargs={'options': {'strings_to_numbers': True}})
            for idx, x in report_config_df.iterrows():
                if mode_of_generation != "tracker":
                    report_dict = []

                report_name = str(x['name'])
                start_date = each_endpoint["default_start_date"]
                end_date = datetime.today()
                report_frequency = str(x['frequency'])
                periods = self.get_dhis2_period(start_date, end_date, report_frequency)
                report_name = report_name[0:30].strip()
                org_units_name = x["org_units"].split(",")
                print(report_name)
                complete_report_path = os.path.join(base_location, report_name)
                reports_by_name = self.__reports[int(idx)]
                for index, each_report_index in enumerate(reports_by_name):
                    report_to_print = each_report_index['dataValues']
                    report_df = pd.DataFrame.from_dict(report_to_print)
                    print(report_df.head())
                    org_unit_name = org_units_name[index]
                    org_unit_id = org_units_df.loc[org_units_df["Org Unit"] == org_unit_name]["Org Unit Id"].iat[0]

                    for row in periods:
                        split_date = str(row).split("-")
                        period = self.format_dhis2_date(row, report_frequency)
                        row = str(row)[0:10]
                        report_date = datetime.strptime(row, "%Y-%m-%d")

                        report = {
                            "Date": report_date.date(),
                            "facility": org_unit_name,
                            "report name": report_name,
                            "frequency": report_frequency}
                        if report_df.empty:
                            report["report in the system"] = "No"
                            report["entered on time"] = "No"
                        else:
                            test_period = report_df["period"].iat[0]
                            df_x = report_df.loc[
                                (report_df["period"] == period) & (report_df["orgUnit"] == str(org_unit_id))]
                            if df_x.empty:
                                report["report in the system"] = "No"
                                report["entered on time"] = "No"
                            else:
                                report["report in the system"] = "Yes"
                                date_created_str = df_x["created"].iat[0]
                                date_created_str = date_created_str[0:10]
                                date_format = "%Y-%m-%d"

                                # Convert string to datetime using strptime
                                expected_entry_date = report_date + timedelta(days=report_due_day)
                                date_created = datetime.strptime(date_created_str, date_format)
                                days_diff = (date_created - expected_entry_date).days
                                if days_diff <= 0:
                                    report["entered on time"] = "Yes"
                                else:
                                    report["entered on time"] = "No"
                                report["date entered in system"] = date_created.date()
                                report["days difference from due date"] = days_diff

                                if mode_of_generation != "tracker":
                                    for key, data_element_series in df_x.iterrows():
                                        data_values = data_element_series.to_dict()
                                        value = data_values['value']
                                        data_element = data_values['dataElement']
                                        column_name = data_elements_df.loc[data_elements_df["Data Element Id"] ==
                                                                           data_element]["Data Element"].iat[0]
                                        if "categoryOptionCombo" in data_values:
                                            category_option_combo = data_values["categoryOptionCombo"]
                                            category_option_combo_name = category_option_combinations_df.loc[
                                                category_option_combinations_df["id"] == category_option_combo][
                                                "name"].iat[0]
                                            report[str(column_name) + " " + str(category_option_combo_name)] = value
                                        else:
                                            report[column_name] = value

                        report_dict.append(report)
                    if mode_of_generation != "tracker":
                        final_df = pd.DataFrame.from_records(report_dict)
                        final_df.to_excel(writer, index=False, sheet_name=report_name)
            if mode_of_generation != "tracker":
                writer.close()
            if mode_of_generation == "tracker":
                final_df = pd.DataFrame.from_records(report_dict)
                final_df.to_excel(writer, index=False, sheet_name=report_file)
                writer.close()
            print("Ending time" + str(datetime.now()))
