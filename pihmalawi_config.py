config = {
    "base_file_path": "./DHIS2 report",
    # tracker=DHIS2 Reporting Summary, full=DHIS2 Full Report
    "report_generation": "tracker",
    "tracker_file_name": "DHIS2 Reporting Summary",
    "full_report_file_name": "DHIS2 Full Report",
    "data_elements_file_name": "data_elements.csv",
    "org_units_file_name": "org_units.csv",
    "category_option_combinations": "category_option_combinations.csv",
    "endpoints": [
        {
            "base": "",
            "username": "",
            "password": "",
            "report_file_name": "reports.csv",
            "use_start_date_in_request": True,
            "use_end_date_in_request": True,
            "default_start_date": "2018-01-01",
            "default_end_date": "2023-06-30",
        },
    ],
}
