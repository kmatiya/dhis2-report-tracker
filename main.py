# This is a sample Python script.
from api.FolderCreator import FolderCreator
from api.HttpReportService import HttpReportService
from api.ReportGenerator import ReportGenerator
# from config import config
# if using pihmalawi
from pihmalawi_config import config

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    http_report_service = HttpReportService(config)
    print("Creating report Folders successfully")
    print("Pulling reports from server has started")
    http_report_service.get_reports_from_server()
    report_generator = ReportGenerator(http_report_service.get_reports(), config)
    report_generator.get_data_frame()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
