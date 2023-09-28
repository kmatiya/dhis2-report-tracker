from api.HttpReportService import HttpReportService
from api.ReportGenerator import ReportGenerator
from api.DbService import DbService
from datetime import datetime
# from config import config
# if using pihmalawi
from pihmalawi_config import config

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Starting time" + str(datetime.now()))
    http_report_service = HttpReportService(config)
    print("Creating report Folders successfully")
    print("Pulling reports from server has started")
    http_report_service.get_reports_from_server()
    report_generator = ReportGenerator(http_report_service.get_reports(), config)
    tracker_final_df, conditions_check_df = report_generator.get_data_frame()
    for each_config in config["endpoints"]:
        db_service = DbService(database=each_config["db_name"], user=each_config["db_user"], password=each_config['db_password'],
                               host=each_config['db_host'],
                               port=each_config["db_port"])
        db_service.write_to_db("dhis2_report_summary", tracker_final_df)
        db_service.write_to_db("data_element_validation", conditions_check_df)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
