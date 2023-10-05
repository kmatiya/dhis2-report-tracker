import pandas as pd
from datetime import datetime, timedelta
from datetime import date
import os
import os.path
from copy import deepcopy


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
        date_format = "%Y-%m-%d"
        date_and_time_format = "%Y-%m-%d %H:%M:%S"
        conditions_df = pd.read_csv("conditions.csv")
        conditions_check = []
        tracker_report_file = self.__config["tracker_file_name"]
        file_name = tracker_report_file + '.xlsx'
        tracker_writer = pd.ExcelWriter(file_name,
                                        engine='xlsxwriter',
                                        engine_kwargs={'options': {'strings_to_numbers': True}})
        tracker_report_dict = []
        base_location = self.__config["base_file_path"]
        data_elements_df = pd.read_csv(self.__config["data_elements_file_name"])
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        category_option_combinations_df = pd.read_csv(self.__config["category_option_combinations"],encoding='latin1')
        print("Create files for each report")

        for each_endpoint in self.__config["endpoints"]:
            report_config_df = pd.read_csv(each_endpoint["report_file_name"])
            report_file = self.__config["full_report_file_name"]
            file_name = report_file + '.xlsx'
            full_report_writer = pd.ExcelWriter(file_name,
                                                engine='xlsxwriter',
                                                engine_kwargs={'options': {'strings_to_numbers': True}})
            for idx, x in report_config_df.iterrows():
                full_report_dict = []
                report_name = str(x['name'])
                start_date = each_endpoint["default_start_date"]
                end_date = datetime.today()
                end_date_str = datetime.strftime(datetime.now(), date_and_time_format)
                report_due_day = x["report_due_day"]
                report_frequency = str(x['frequency'])
                data_set = str(x["data_set"])
                periods = self.get_dhis2_period(start_date, end_date, report_frequency)
                report_name = report_name[0:30].strip()
                org_units_name = x["org_units"].split(",")
                complete_report_path = os.path.join(base_location, report_name)
                reports_by_name = self.__reports[int(idx)]
                for index, each_report_index in enumerate(reports_by_name):
                    report_to_print = each_report_index['dataValues']
                    report_df = pd.DataFrame.from_dict(report_to_print)
                    org_unit_name = org_units_name[index]
                    org_unit_id = org_units_df.loc[org_units_df["Org Unit"] == org_unit_name]["Org Unit Id"].iat[0]

                    for row in periods:
                        split_date = str(row).split("-")
                        period = self.format_dhis2_date(row, report_frequency)
                        row = str(row)[0:10]
                        report_date = datetime.strptime(row, date_format)
                        full_report = {}
                        print(f"Processing {report_name} at {org_units_name} for date: {report_date.date()}")
                        report = {
                            "date": report_date.date(),
                            "facility": org_unit_name,
                            "report_name": report_name,
                            "date_created_in_db": end_date_str,
                            "frequency": report_frequency}
                        if report_df.empty:
                            report["report_in_the_system"] = "No"
                            report["entered_on_time"] = "No"
                            tracker_report_dict.append(report)
                            full_report_dict.append(full_report)
                        else:
                            test_period = report_df["period"].iat[0]
                            df_x = report_df.loc[
                                (report_df["period"] == period) & (report_df["orgUnit"] == str(org_unit_id))]
                            if df_x.empty:
                                report["report_in_the_system"] = "No"
                                report["entered_on_time"] = "No"
                                tracker_report_dict.append(report)
                                full_report_dict.append(full_report)
                            else:
                                report["report_in_the_system"] = "Yes"
                                date_created_str = df_x["created"].iat[0]
                                date_created_str = date_created_str[0:10]


                                # Convert string to datetime using strptime
                                expected_entry_date = report_date + timedelta(days=report_due_day)
                                date_created = datetime.strptime(date_created_str, date_format)
                                days_diff = (date_created - expected_entry_date).days
                                if days_diff <= 0:
                                    report["entered_on_time"] = "Yes"
                                else:
                                    report["entered_on_time"] = "No"
                                report["date_entered_in_system"] = date_created.date()
                                report["days_difference_from_due_date"] = days_diff

                                report_conditions = conditions_df.loc[(conditions_df["data_set"] == data_set) &
                                                                      (conditions_df[
                                                                           "facility"] == org_unit_name)]

                                if not report_conditions.empty:
                                    for a, each_condition in report_conditions.iterrows():
                                        is_null = "Yes"
                                        is_lower = ""
                                        is_upper = ""
                                        value = ''

                                        column_name = each_condition["Data Element"]
                                        condition = each_condition["Data Element Id"]
                                        category_option_combo_id = str(each_condition["category_option_combo_id"])
                                        category_option_combo_name = str(each_condition["category_option_combo_name"])
                                        df_x_filtered = df_x[df_x['dataElement'] == condition]
                                        if not df_x_filtered.empty:
                                            if category_option_combo_id.strip().lower() != 'nan':
                                                column_name = column_name + " " + category_option_combo_name
                                                df_x_filtered = df_x[
                                                    df_x['categoryOptionCombo'] == category_option_combo_id]

                                            is_null = "No"
                                            value = float(df_x_filtered['value'].iat[0])
                                            lower_bound = float(each_condition["lower_bound"])
                                            upper_bound = float(each_condition["upper_bound"])
                                            if value <= lower_bound and is_null == "No":
                                                is_lower = "Yes"
                                            else:
                                                is_lower = "No"
                                            if value >= upper_bound and is_null == "No":
                                                is_upper = "Yes"
                                            else:
                                                is_upper = "No"

                                        conditions_check.append({
                                            "date": report_date.date(),
                                            "facility": org_unit_name,
                                            "report_name": report_name,
                                            "frequency": report_frequency,
                                            "data_element": column_name,
                                            "is_lower": is_lower,
                                            "is_upper": is_upper,
                                            "is_null": is_null,
                                            "value": value,
                                            "date_created_in_db": end_date_str
                                        })

                                full_report = deepcopy(report)
                                for key, data_element_series in df_x.iterrows():
                                    data_values = data_element_series.to_dict()
                                    value = data_values['value']
                                    each_condition = data_values['dataElement']
                                    column_name = data_elements_df.loc[data_elements_df["Data Element Id"] ==
                                                                       each_condition]["Data Element"].iat[0]

                                    if "categoryOptionCombo" in data_values:
                                        category_option_combo = data_values["categoryOptionCombo"]
                                        category_option_combo_name = category_option_combinations_df.loc[
                                            category_option_combinations_df["id"] == category_option_combo][
                                            "name"].iat[0]
                                        full_report[str(column_name) + " " + str(category_option_combo_name)] = value
                                    else:
                                        full_report[column_name] = value
                                tracker_report_dict.append(report)
                                full_report_dict.append(full_report)

                    full_report_final_df = pd.DataFrame.from_records(full_report_dict)
                    full_report_final_df.to_excel(full_report_writer, index=False, sheet_name=report_name)
            full_report_writer.close()
            tracker_final_df = pd.DataFrame.from_records(tracker_report_dict)
            tracker_final_df.to_excel(tracker_writer, index=False, sheet_name=tracker_report_file)
            tracker_writer.close()
            # New code to export conditions_check as Excel file
            conditions_check_df = pd.DataFrame(conditions_check)
            conditions_check_df.to_excel("conditions_check.xlsx", index=False)

            print("Ending time" + str(datetime.now()))
            return tracker_final_df, conditions_check_df
