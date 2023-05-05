config = {
    "base_file_path": "./DHIS2 report",
    "file_name": "DHIS2",
    "data_elements_file_name": "data_elements.csv",
    "org_units_file_name": "org_units.csv",
    "periods_file_name": "periods.csv",
    "endpoints": [
        {
            "base": "",
            "username": "",
            "password": "",
            "use_start_date_in_request": True,
            "use_end_date_in_request": True,
            "default_start_date": "2020-01-01",
            "default_end_date": "2023-06-30",
            "org_units": [
                {
                    "id": "Rmh4wKR794k",
                    "name": "Neno District Hospital"
                },
                {
                    "id": "jBJ1nrUXKIu",
                    "name": "Lisungwi Community hospital"
                }
            ],
        },
    ],
    "reports": [
        {
            "resource": "/dataValueSets",
            "dataSet": "XttTY8YbYKB",
            "name": "Clerks reports",
            "assigned_to": "Bright",
            "org_units": [
                {
                    "id": "Rmh4wKR794k",
                    "name": "Neno District Hospital"
                },
                {
                    "id": "jBJ1nrUXKIu",
                    "name": "Lisungwi Community hospital"
                }
            ],
            "column_order": [
                 "NX9ITIOkqCw", "poyokFLTPMo", "WYUB8EK3P02",
            ]
        },
    ]
}
