import pandas as pd
from datetime import datetime
from datetime import date
import os
import os.path


class ReportGenerator:
    def __init__(self, reports, config):
        self.__reports = reports
        self.__config = config

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
            start_date = each_endpoint["default_start_date"]
            end_date = datetime.today()
            periods = pd.date_range(start_date, end_date, freq="M").to_list()
            report_config_df = pd.read_csv(each_endpoint["report_file_name"])
            org_units_name = report_config_df["org_units"].tolist()[0].split(",")
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
                report_name = report_name[0:30].strip()
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
                        period = split_date[0] + split_date[1]
                        report_date = row.strftime("%d/%m/%Y")

                        report = {
                            "Date": report_date,
                            "facility": org_unit_name,
                            "report name": report_name}
                        if report_df.empty:
                            if mode_of_generation == "tracker":
                                report["report in the system"] = "No"
                                report["entered on time"] = "No"
                        else:
                            df_x = report_df.loc[
                                (report_df["period"] == period) & (report_df["orgUnit"] == str(org_unit_id))]
                            if df_x.empty:
                                if mode_of_generation == "tracker":
                                    report["report in the system"] = "No"
                                    report["entered on time"] = "No"
                            else:
                                if mode_of_generation == "tracker":
                                    report["report in the system"] = "Yes"
                                    date_created_str = df_x["created"].iat[0]
                                    date_created_str = date_created_str[0:10]
                                    date_format = "%Y-%m-%d"

                                    # Convert string to datetime using strptime
                                    date_created = datetime.strptime(date_created_str, date_format)
                                    day_created = date_created.day
                                    if day_created <= report_due_day:
                                        report["entered on time"] = "Yes"
                                    else:
                                        report["entered on time"] = "No"
                                    report["date entered in system"] = date_created_str
                                    report["days difference from due date"] = day_created - report_due_day

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
                                                category_option_combinations_df["id"] == category_option_combo]["name"].iat[0]
                                            report[column_name + " " + category_option_combo_name] = value
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
