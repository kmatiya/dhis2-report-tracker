from app import app

from flask import Flask, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from app.DbService import DbService
from app.config import config

auth = HTTPBasicAuth()

users = config["users"]
for each_user in users:
    users[each_user] = generate_password_hash(users[each_user])
db_config = config["db_config"]

db_service = DbService(database=db_config["db_name"], user=db_config["db_user"],
                       password=db_config["db_password"],
                       host=db_config["db_host"],
                       port=db_config["db_port"])

data_elements_df = db_service.get_from_db("data_elements")
category_option_combinations_df = db_service.get_from_db("category_option_combinations")


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/<table_name>')
@auth.login_required
def index(table_name):
    try:
        table_df = db_service.get_from_db(table_name)
        table_df = table_df.replace([None], "")
        report_element_columns = table_df.columns.tolist()[9:]
        for each_column_name in report_element_columns:
            column_list = str(each_column_name).split("_")
            if len(column_list) == 1:
                data_element = data_elements_df[data_elements_df["id"] == column_list[0]]["name"].iat[0]
                table_df.rename(columns={each_column_name: data_element}, inplace=True)
            else:
                data_element = data_elements_df[data_elements_df["id"] == column_list[0]]["name"].iat[0]
                category_option_combination = category_option_combinations_df[category_option_combinations_df["id"] ==
                                                                              column_list[1]]["name"].iat[0]
                if category_option_combination is None:
                    table_df.rename(columns={each_column_name: data_element + " None"}, inplace=True)
                else:
                    table_df.rename(columns={each_column_name: f"{data_element} {category_option_combination}"},
                                    inplace=True)
        return table_df.to_html()
    except:
        abort(500)


'''@app.route('/')
@auth.login_required
def index():
    hmis_15_df = db_service.get_from_db("hmis_15")
    report_element_columns = hmis_15_df.columns.tolist()[9:]
    for each_column_name in report_element_columns:
        column_list = str(each_column_name).split("_")
        if len(column_list) == 1:
            data_element = data_elements_df[data_elements_df["id"] == column_list[0]]["name"].iat[0]
            hmis_15_df.rename(columns={each_column_name: data_element}, inplace=True)
        else:
            data_element = data_elements_df[data_elements_df["id"] == column_list[0]]["name"].iat[0]
            category_option_combination = category_option_combinations_df[category_option_combinations_df["id"] ==
                                                                          column_list[1]]["name"].iat[0]
            if category_option_combination is None:
                hmis_15_df.rename(columns={each_column_name: data_element + " None"}, inplace=True)
            else:
                hmis_15_df.rename(columns={each_column_name: f"{data_element} {category_option_combination}"},
                                  inplace=True)
    report = []
    for index, each_row in hmis_15_df.iterrows():
        # print(each_row.to_json())
        report.append(each_row.to_json())
    return report'''
