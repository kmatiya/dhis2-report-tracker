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
        file_name = self.__config["file_name"] + '.xlsx'
        writer = pd.ExcelWriter(file_name,
                                engine='xlsxwriter',
                                engine_kwargs={'options': {'strings_to_numbers': True}})
        base_location = self.__config["base_file_path"]
        data_elements_df = pd.read_csv(self.__config["data_elements_file_name"])
        periods_df = pd.read_csv(self.__config["periods_file_name"])
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        print("Create files for each report")
        for idx, x in enumerate(self.__config["reports"]):
            report_name = str(x['name'])
            complete_report_path = os.path.join(base_location, report_name)
            reports_by_name = self.__reports[int(idx)]
            report_dict = []
            for index, each_report_index in enumerate(reports_by_name):
                report_to_print = each_report_index['dataValues']
                report_df = pd.DataFrame.from_dict(report_to_print)
                print(report_df.head())
                org_unit_id = x["org_units"][index]["id"]
                for index, row in periods_df.iterrows():
                    report = {
                        "Date": row["date"],
                        "facility":
                            org_units_df.loc[org_units_df["Org Unit Id"] == str(org_unit_id)]["Org Unit"].iat[0]
                    }
                    df_x = report_df.loc[
                        (report_df["period"] == str(row["period"])) & (report_df["orgUnit"] == str(org_unit_id))]
                    if df_x.empty:
                        report["report in the system"] = "No"
                        for data_element in x["column_order"]:
                            value = ""
                            column_name = data_elements_df.loc[data_elements_df["Data Element Id"] == data_element][
                                "Data Element"].iat[0]
                            report[column_name] = value
                    else:
                        report["report in the system"] = "Yes"
                        for data_element in x["column_order"]:
                            value = df_x.loc[df_x["dataElement"] == data_element]["value"].iat[0]
                            column_name = data_elements_df.loc[data_elements_df["Data Element Id"] == data_element][
                                "Data Element"].iat[0]
                            report[column_name] = value
                            print(df_x.head())
                    report_dict.append(report)
            final_df = pd.DataFrame.from_records(report_dict)
            final_df.to_excel(writer, index=False, sheet_name=report_name)

        writer.close()
