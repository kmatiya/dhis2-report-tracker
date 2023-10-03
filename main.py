import time

from api.HttpReportService import HttpReportService
from api.ReportGenerator import ReportGenerator
from api.DbService import DbService
from datetime import datetime
# from config import config
# if using pihmalawi
from pihmalawi_config import config
import schedule


def generate_reports():

    print("Starting time" + str(datetime.now()))
    http_report_service = HttpReportService(config)
    print("Pulling reports from server has started")
    http_report_service.get_reports_from_server()
    print("Complete pulling reports from DHIS2 api")
    status_code, reports = http_report_service.get_reports()
    if status_code == 200:
        report_generator = ReportGenerator(reports, config)
        tracker_final_df, conditions_check_df = report_generator.get_data_frame()
        print("Complete generating reports")
        for each_config in config["endpoints"]:
            db_service = DbService(database=each_config["db_name"], user=each_config["db_user"],
                                   password=each_config['db_password'],
                                   host=each_config['db_host'],
                                   port=each_config["db_port"])
            db_service.write_to_db("dhis2_report_summary", tracker_final_df)
            db_service.write_to_db("data_element_validation", conditions_check_df)
        print("Ending saving in database at " + str(datetime.now()))
    else:
        print("There was an error getting reports from the server")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    generate_reports()
    '''print("starting scheduled tasks")
    schedule.every(4).hours.do(generate_reports)
    # Loop so that the scheduling task
    # keeps on running all time.
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)'''

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
