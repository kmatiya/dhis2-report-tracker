import time
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

time.sleep(config["time_delay"])


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/<table_name>')
@auth.login_required
def index(table_name):
    try:
        data_elements_df = db_service.get_from_db("data_elements")
        category_option_combinations_df = db_service.get_from_db("category_option_combinations")
        # if table_name == "family_planning_monthly_pbi" or table_name == "epi_monthly_pbi":
        if table_name[-4:] == "_pbi":
            table_name =table_name.replace("_pbi","")
            db_columns = config["db_columns"][table_name]
            column_values = list(db_columns.values())
            table_df = db_service.get_from_db_by_columns(table_name, column_values)
        else:
            table_df = db_service.get_from_db(table_name)
        report_element_columns = table_df.columns.tolist()[9:]
        table_df = table_df.replace([None], "")
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