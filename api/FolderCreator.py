# importing os module
import os


class FolderCreator:
    def __init__(self, config):
        self.__config = config

    def create_report_folders(self):
        base_location = self.__config["base_file_path"]
        if not os.path.exists(base_location):
            os.mkdir(base_location)
        print(len(self.__config['reports']))
        for each_report in self.__config['reports']:
            # complete_base_location = base_location + "/" + each_report['prefix']
            complete_base_location = os.path.join(base_location, str(each_report['prefix']))
            try:

                if not os.path.exists(complete_base_location):
                    os.mkdir(complete_base_location)
                # Leaf directory
                report_directory = complete_base_location + "/" + each_report['name']
                if not os.path.exists(report_directory):
                    os.mkdir(report_directory)
            except Exception as error:
                print(error)
