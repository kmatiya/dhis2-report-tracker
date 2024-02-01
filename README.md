# Background
With the growth in the demand for data analysis and visualization for data stored in DHIS2, we have a solution that can ease this process through the use of APZU’s data warehouse. This solution is scalable and can connect to any DHIS2 instance for DHIS2 Aggregate.  

# Overview Of Implementation
![image](https://github.com/kmatiya/dhis2-report-tracker/assets/37307114/55e20d94-81d3-42f5-b4a1-25b9d816e4eb)

Once the data is pulled from the server, it is transformed longitudinally for easy data analysis and stored in a Postgres Database. By default, this database creates the following tables:
-  dhis2_report_summary – This table stores the summary of reports that were captured in the DHIS2 system and the time that they were captured in the system to easily calculate timeliness and completeness. Unlike the DHIS2 calculation, this tables tracks a report to be in the system only if there are data elements available for that report
-  data_elements – stores data elements as meta-data
-  category_option_combinations – stores category option combinations as meta-data
-  data_element_validation – Monitors data quality of reports based on the configuration in the python script.
-  datasets – These are the reports configured to be pulled from the DHIS2 instance. With data element column names being long, column names are stored by data element id separated by an underscore (_) for the category option combination id. Figure below illustrates a sample dataset for anc_monthly report
-  For the tables for dhis2_report_summary, data_elements, category_option_combinations, data_element_validation, Power BI or any third party application can to connect to these tables with no need for further analysis of the data in the tables.
-  For the datasets / reports, these can be connected the same way explained in f but the challenge will be translating the columns into a readable format. The solution to this, a web service was developed to handle translating the columns into a readable format which Power BI and any third party application can connect to.

# Installation
**Install Docker**
-  Install docker by following this [link](https://docs.docker.com/engine/install/)
**Install docker-compose**
**Get Report Tracker Repository**
-  git clone https://github.com/kmatiya/dhis2-report-tracker/
-  Configure repository
-  cd dhis2-report-tracker
-  open pihmalawi_config.py add DHIS2 API URL, username and password
**Build Docker Images**
-  docker-compose build -f dhis2-docker-compose.yml
**Run Docker Containers**
-  docker-compose up -d
