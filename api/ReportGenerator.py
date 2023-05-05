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
        report_file = self.__config["file_name"]
        file_name = report_file + '.xlsx'
        writer = pd.ExcelWriter(file_name,
                                engine='xlsxwriter',
                                engine_kwargs={'options': {'strings_to_numbers': True}})
        base_location = self.__config["base_file_path"]
        data_elements_df = pd.read_csv(self.__config["data_elements_file_name"])
        periods_df = pd.read_csv(self.__config["periods_file_name"])
        org_units_df = pd.read_csv(self.__config["org_units_file_name"])
        print("Create files for each report")
        report_dict = []
        for each_endpoint in self.__config["endpoints"]:
            reports_df = pd.read_csv(each_endpoint["report_file_name"])
            org_units_name = reports_df["org_units"].tolist()[0].split(",")
            for idx, x in reports_df.iterrows():
                report_name = str(x['name'])
                print(report_name)
                complete_report_path = os.path.join(base_location, report_name)
                reports_by_name = self.__reports[int(idx)]
                for index, each_report_index in enumerate(reports_by_name):
                    report_to_print = each_report_index['dataValues']
                    report_df = pd.DataFrame.from_dict(report_to_print)
                    print(report_df.head())
                    org_unit_name = org_units_name[index]
                    org_unit_id = org_units_df.loc[org_units_df["Org Unit"] == org_unit_name]["Org Unit Id"].iat[0]
                    for index, row in periods_df.iterrows():
                        report = {
                            "Date": row["date"],
                            "facility": org_unit_name}
                        if report_df.empty:
                            report["report in the system"] = "No"
                            report["report"] = report_name

                        else:
                            df_x = report_df.loc[
                            (report_df["period"] == str(row["period"])) & (report_df["orgUnit"] == str(org_unit_id))]
                            if df_x.empty:
                                report["report in the system"] = "No"
                                report["report"] = report_name
                            else:
                                report["report in the system"] = "Yes"
                                report["report"] = report_name
                        report_dict.append(report)
            final_df = pd.DataFrame.from_records(report_dict)
            final_df.to_excel(writer, index=False, sheet_name=report_file)

            writer.close()