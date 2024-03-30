import pandas as pd

from utils.PathManager import load_path_manager as lpm

file_master_data = lpm.input("API Test Master Data.xlsx")


def make_hyperlink(link, value):
    return f'=HYPERLINK("{link}", "{value}")'


if __name__ == '__main__':

    sheets_dict = pd.read_excel(file_master_data, sheet_name=None)
    writer = pd.ExcelWriter(file_master_data.replace('.xlsx', ' (hyperlink).xlsx'), engine="openpyxl")

    for name, sheet in sheets_dict.items():
        if sheet.empty or name == "README" or name == "MASTER":
            sheet.to_excel(writer, index=False, sheet_name=name)
            continue

        for index, row in sheet.iterrows():

            if row['API ID'] == 'API-007':
                api_result_file_path_link = f"API-Result/{row['API ID']}/{row['Scenario']}.png"
            else:
                api_result_file_path_link = f"API-Result/{row['API ID']}/{row['Scenario']}.txt"
            sheet.at[index, "Response File Path"] = api_result_file_path_link
            sheet.at[index, "Response File"] = make_hyperlink(api_result_file_path_link, "API Result")

            sql_statement_file_path_link = f"SQL-Statement/{row['API ID']}/{row['Scenario']}.txt"
            sheet.at[index, "SQL Path"] = sql_statement_file_path_link
            sheet.at[index, "SQL"] = make_hyperlink(sql_statement_file_path_link, "SQL Statement")

            jaeger_file_path_link = f"Jaeger-Screenshot/{row['API ID']}/{row['Scenario']}.png"
            sheet.at[index, "Jaeger Screenshot Path"] = jaeger_file_path_link
            sheet.at[index, "Jaeger Screenshot"] = make_hyperlink(jaeger_file_path_link, "Jaeger Screenshot")

            junit_file_path_link = f"Junit-Screenshot/{row['API ID']}/{row['Scenario']}.png"
            sheet.at[index, "JUnit Test Screenshot Path"] = junit_file_path_link
            sheet.at[index, "JUnit Test Screenshot"] = make_hyperlink(junit_file_path_link, "Junit Screenshot")

        sheet.to_excel(writer, index=False, sheet_name=name)

    writer.save()
