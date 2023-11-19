import pandas as pd
from datetime import datetime, timedelta
from datetime import date
import os
import os.path
from copy import deepcopy
from api.DbService import DbService


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

    def get_data_frame(self, data_elements, category_option_combos, db_service: DbService):
        date_format = "%Y-%m-%d"
        date_and_time_format = "%Y-%m-%d %H:%M:%S"
        conditions_check = []
        tracker_report_file = self.__config["tracker_file_name"]
        file_name = tracker_report_file + '.xlsx'
        tracker_writer = pd.ExcelWriter(file_name,
                                        engine='xlsxwriter',
                                        engine_kwargs={'options': {'strings_to_numbers': True}})
        tracker_report_dict = []
        base_location = self.__config["base_file_path"]
        data_elements_df = pd.DataFrame.from_dict(data_elements)
        data_elements_df.rename(columns={'displayName': 'name'}, inplace=True)
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        category_option_combinations_df = pd.DataFrame.from_dict(category_option_combos)
        category_option_combinations_df.rename(columns={'displayName': 'name'}, inplace=True)
        print("Create files for each report")

        for each_endpoint in self.__config["endpoints"]:
            report_config_df = pd.read_csv(each_endpoint["report_file_name"])
            report_file = self.__config["full_report_file_name"]
            conditions_df = pd.read_csv(each_endpoint["element_validation_config"])
            file_name = report_file + '.xlsx'
            full_report_writer = pd.ExcelWriter(file_name,
                                                engine='xlsxwriter',
                                                engine_kwargs={'options': {'strings_to_numbers': True}})

            for idx, x in report_config_df.iterrows():
                full_report_dict = []
                report_name = str(x['name'])
                report_short_name = str(x['short_name'])
                start_date = each_endpoint["default_start_date"]
                end_date = datetime.today()
                end_date_str = datetime.strftime(datetime.now(), date_and_time_format)
                report_due_day = x["report_due_day"]
                report_frequency = str(x['frequency'])
                data_set = str(x["data_set"])
                periods = self.get_dhis2_period(start_date, end_date, report_frequency)
                report_name = report_name[0:30].strip()
                org_units_name = x["org_units"].split(",")
                reports_by_name = self.__reports[int(idx)]
                for index, each_report_index in enumerate(reports_by_name):
                    report_to_print = each_report_index['dataValues']
                    report_df = pd.DataFrame.from_dict(report_to_print)
                    org_unit_name = org_units_name[index]
                    org_unit_id = org_units_df.loc[org_units_df["Org Unit"] == org_unit_name]["Org Unit Id"].iat[0]

                    for row in periods:
                        period = self.format_dhis2_date(row, report_frequency)
                        row = str(row)[0:10]
                        report_date = datetime.strptime(row, date_format)
                        full_report = {}
                        print(f"Processing {report_name} at {org_unit_name} for date: {report_date.date()}")
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
                                full_report = deepcopy(report)
                                for key, data_element_series in df_x.iterrows():
                                    data_values = data_element_series.to_dict()
                                    value = data_values['value']
                                    data_element = data_values["dataElement"]
                                    column_name = data_elements_df.loc[data_elements_df["id"] ==
                                                                       data_element]["name"].iat[0]
                                    if "categoryOptionCombo" in data_values:
                                        category_option_combo = data_values["categoryOptionCombo"]
                                        category_option_combo_name = \
                                            category_option_combinations_df.loc[category_option_combinations_df["id"] ==
                                                                                data_element]["name"].iat[0]
                                        column_name = column_name + " " + category_option_combo_name
                                        full_report[str(data_element) + "_" + str(category_option_combo)] = value
                                        if each_endpoint["validate_elements"] is True:
                                            element_validation_condition = conditions_df.loc[
                                                (conditions_df["data_set"] == data_set) &
                                                (conditions_df[
                                                     "facility"] == org_unit_name) &
                                                (conditions_df[
                                                     "data_element_id"] == data_element) &
                                                (conditions_df["category_option_combo_id"] == category_option_combo)
                                                ]
                                            if not element_validation_condition.empty:
                                                is_null, is_lower, is_upper = self.validate_element_conditions(
                                                    element_validation_condition.iat[0], value)
                                                self.update_condition_checks(column_name, conditions_check,
                                                                             end_date_str, is_lower,
                                                                             is_null, is_upper, org_unit_name,
                                                                             report_date,
                                                                             report_frequency, report_name, value)
                                    else:
                                        full_report[data_element] = value
                                        if each_endpoint["validate_elements"] is True:
                                            element_validation_condition = \
                                                conditions_df.loc[(conditions_df["data_set"] == data_set) &
                                                                  (conditions_df[
                                                                       "facility"] == org_unit_name) &
                                                                  (conditions_df[
                                                                       "data_element_id"] == data_element)
                                                                  ]
                                            if not element_validation_condition.empty:
                                                is_null, is_lower, is_upper = self.validate_element_conditions(
                                                    element_validation_condition.iat[0], value)
                                                self.update_condition_checks(column_name, conditions_check,
                                                                             end_date_str,
                                                                             is_lower,
                                                                             is_null, is_upper, org_unit_name,
                                                                             report_date,
                                                                             report_frequency, report_name, value)
                                tracker_report_dict.append(report)
                                full_report_dict.append(full_report)
                    full_report_final_df = pd.DataFrame.from_records(full_report_dict)
                    db_service.write_to_db(report_short_name, full_report_final_df)
                    full_report_final_df.to_excel(full_report_writer, index=False, sheet_name=report_name)
            full_report_writer.close()
            tracker_final_df = pd.DataFrame.from_records(tracker_report_dict)
            tracker_final_df.to_excel(tracker_writer, index=False, sheet_name=tracker_report_file)
            tracker_writer.close()
            # New code to export conditions_check as Excel file
            conditions_check_df = pd.DataFrame(conditions_check)
            if each_endpoint["validate_elements"] is True:
                conditions_check_df.to_excel("conditions_check.xlsx", index=False)
                db_service.write_to_db("data_element_validation", conditions_check_df)
            db_service.write_to_db("dhis2_report_summary", tracker_final_df)
            db_service.write_to_db("data_elements", data_elements_df)
            db_service.write_to_db("category_option_combinations", category_option_combinations_df)
            print("Ending time" + str(datetime.now()))

    def update_condition_checks(self, column_name, conditions_check, end_date_str, is_lower, is_null, is_upper,
                                org_unit_name,
                                report_date, report_frequency, report_name, value):
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

    def validate_element_conditions(self, element_validation_condition, value):
        is_null = "Yes"
        is_lower = ""
        is_upper = ""
        if str(element_validation_condition["validate_lower_bound"]).lower() == "yes":
            is_null = "No"
            lower_bound = float(element_validation_condition["lower_bound"])
            if value <= lower_bound and is_null == "No":
                is_lower = "Yes"
            else:
                is_lower = "No"

        if str(element_validation_condition["validate_lower_bound"]).lower() == "yes":
            is_null = "No"
            upper_bound = float(element_validation_condition["upper_bound"])
            if value >= upper_bound and is_null == "No":
                is_upper = "Yes"
            else:
                is_upper = "No"
        return is_null, is_lower, is_upper
