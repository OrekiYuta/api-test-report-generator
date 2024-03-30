import os
import json
import time
import uuid
import shutil
import requests
import textwrap
import sqlparse
import pandas as pd

from sql_metadata import Parser
# from selenium.webdriver.common.by import By
from urllib3.exceptions import InsecureRequestWarning

import config.secret as secret
from utils.PathManager import load_path_manager as lpm
from utils.ChromeDriverManager import ChromeDriverManager

# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

folder_input_api_result = str(lpm.input("API-Result"))
folder_input_api_result_link = "API-Result"

folder_input_jaeger = str(lpm.input("Jaeger-Screenshot"))
folder_input_jaeger_link = "Jaeger-Screenshot"

folder_input_sql_statement = str(lpm.input("SQL-Statement"))
folder_input_sql_statement_link = "SQL-Statement"

folder_input_junit = str(lpm.input("Junit-Screenshot"))

file_master_data = lpm.input("API Test Master Data.xlsx")
file_token = lpm.config("user_token.json")

REFRESH_TOKEN = None
BEARER_TOKEN = None

JAEGER_URL = ""
OCP_LOGIN_NAME = ''
OCP_LOGIN_PASSWORD = ''


# def extract_sql_statement_from_jaeger(driver):
#     jpa_data_sources = driver.find_elements(By.XPATH, "//span[text()='jpaDataSource']/../..")
#
#     for data_access_section in jpa_data_sources:
#         current_count = str(len(driver.find_elements(By.CLASS_NAME, 'VirtualizedTraceView--row')))
#         js_click(data_access_section)
#         while str(len(driver.find_elements(By.CLASS_NAME, 'VirtualizedTraceView--row'))) == current_count:
#             time.sleep(0.5)
#
#         jdbc_query_section = data_access_section.find_element(By.XPATH, '../../../../following-sibling::node()')
#         jdbc_query_tag = jdbc_query_section.find_element(By.XPATH, "//span[text()='jdbc.query']/..")
#         js_click(jdbc_query_tag)
#
#     query_elements = jdbc_query_section.find_elements(By.XPATH, "//td[text()='jdbc.query']/../td[2]//span")
#     return list(dict.fromkeys([query.text for query in query_elements]))


def construct_sql_statement_file(statement, row):
    folder_sql_statement_path = f"{folder_input_sql_statement}/{row['API ID']}"
    if not os.path.exists(folder_sql_statement_path):
        os.makedirs(folder_sql_statement_path)

    file_path = f"{folder_sql_statement_path}/{row['Scenario']}.txt"
    file_path_link = f"{folder_input_sql_statement_link}/{row['API ID']}/{row['Scenario']}.txt"

    result_text = ""
    with open(file_path, 'w') as f:
        for query in statement:
            if query.startswith("SELECT") or query.startswith("WITH"):
                result_text += f"-- SELECT from Table(s): [{', '.join(Parser(query).tables)}]\n"
            elif query.startswith("INSERT INTO"):
                result_text += f"-- INSERT into Table: [{', '.join(Parser(query).tables)}]\n"
            elif query.startswith("UPDATE"):
                result_text += f"-- UPDATE Table: [{', '.join(Parser(query).tables)}]\n"
            result_text += sqlparse.format(query, reindent=True, keyword_case='upper')
            result_text += "\n\n"

        for line in result_text.split("\n"):
            if len(line) > 70:
                line = "\n".join(textwrap.wrap(line, width=70))
            f.write(line + "\n")

    return file_path_link


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


# def capture_jaeger_screenshot(driver, row, trace_id):
#     driver.get(f'{JAEGER_URL}/trace/{trace_id.replace("-", "")}')
#
#     driver.execute_script("document.body.style.zoom='50%'")
#
#     folder_jaeger_api_path = f"{folder_input_jaeger}/{row['API ID']}"
#     if not os.path.exists(folder_jaeger_api_path):
#         os.makedirs(folder_jaeger_api_path)
#
#     # screenshot_path = f"{folder_input_jaeger}/{row['API ID']} - {row['Scenario']}.png"
#     screenshot_path = f"{folder_jaeger_api_path}/{row['Scenario']}.png"
#     jaeger_screenshot_path_link = f"{folder_input_jaeger_link}/{row['API ID']}/{row['Scenario']}.png"
#
#     expand_button = driver.find_element(By.CSS_SELECTOR,
#                                         ".anticon.anticon-double-right.TimelineCollapser--btn-expand")
#     js_click(driver, expand_button)
#
#     full_screenshot = chrome_take_full_screenshot(driver)
#
#     with open(folder_input_jaeger + "/" + screenshot_path, 'wb') as f:
#         f.write(full_screenshot)
#
#     return jaeger_screenshot_path_link


def make_hyperlink(link, value):
    return f'=HYPERLINK("{link}", "{value}")'


def chrome_take_full_screenshot(driver):
    def send(cmd, params):
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

        def evaluate(script):
            response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
            return response['result']['value']

        metrics = evaluate( \
            "({" + \
            "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," + \
            "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," + \
            "deviceScaleFactor: window.devicePixelRatio || 1," + \
            "mobile: typeof window.orientation !== 'undefined'" + \
            "})")
        send('Emulation.setDeviceMetricsOverride', metrics)
        screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
        send('Emulation.clearDeviceMetricsOverride', {})

        return base64.b64decode(screenshot['data'])


def get_chrome_auto_download_token_file():
    download_dir = os.path.expanduser("~") + "/Downloads"

    source_file = os.path.join(download_dir, "user_token.json")

    if os.path.exists(source_file):

        target_file = file_token
        shutil.move(source_file, target_file)

        print(f"first run, success get chrome auto download token in file:{target_file}")
    else:
        pass


def load_token_data():
    try:
        with open(file_token, 'r') as file:
            token_data = json.load(file)
            return token_data.get("refresh_token"), token_data.get("access_token")
    except FileNotFoundError:
        return None, None


def init_local_token():
    global REFRESH_TOKEN, BEARER_TOKEN
    REFRESH_TOKEN, BEARER_TOKEN = load_token_data()


def refresh_token():
    url = ""

    global REFRESH_TOKEN
    payload = f'grant_type=refresh_token&refresh_token={REFRESH_TOKEN}&client_id=portal-dev-client'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-type': 'application/x-www-form-urlencoded',
        'Origin': 'https://',
        'Referer': 'https://',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    REFRESH_TOKEN = response.json()["refresh_token"]
    global BEARER_TOKEN
    BEARER_TOKEN = response.json()["access_token"]


def extract_api_result_data(row, trace_id):
    url = row["Request API URL"]
    payload = row["Request Body"]
    path_parameters = row["Path Parameter(s)"]

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Interaction-Id': trace_id,
        'Authorization': f'Bearer {BEARER_TOKEN}',
    }

    # Note temp handle for aa,batch,admin api
    # url = url.replace("https://", "https://")

    # compose path parameters to url
    format_path_parameters = str(path_parameters)
    if format_path_parameters is not None and format_path_parameters != "nan":

        params = format_path_parameters.split(',')
        for param in params:
            key, value = param.split('=')
            placeholder = f'{{{key}}}'
            url = url.replace(placeholder, value)

    format_payload = str(payload)
    if format_payload == "nan" or format_payload is None:
        payload = None

    print(f"[{row['API ID']}] {row['HTTP Method']} {url}\npayload: {payload}")

    response = requests.request(row["HTTP Method"], url, headers=headers, data=payload, verify=False)

    # print(response.text)
    print(f'response http code : {response.status_code}')

    response_json = response.json()
    time.sleep(1)

    api_result_path = f"{folder_input_api_result}/{row['API ID']}"
    api_result_file_path = f"{api_result_path}/{row['Scenario']}.txt"

    text_result = f"{row['HTTP Method']} {url}\n----------\n\n"
    text_result += f"Request header: \n{json.dumps(headers, indent=4)}\n----------\n\n"

    if payload is not None:
        text_result += f"Request body: \n{json.dumps(json.loads(payload), indent=4)}\n----------\n\n"
    else:
        text_result += f"path_parameters: \n{path_parameters}\n----------\n\n"

    text_result += f"Response status: \n{response.status_code}\n----------\n\n"
    text_result += f"Response body: \n{json.dumps(response_json, indent=4)}\n----------\n\n"
    text_result += f"Trace ID: \n{trace_id.replace('-', '')}\n----------\n\n"

    if not os.path.exists(api_result_path):
        os.makedirs(api_result_path)

    with open(api_result_file_path, "w") as file:
        for line in text_result.split("\n"):
            if len(line) > 70:
                line = "\n".join(textwrap.wrap(line, width=70))
            file.write(line + "\n")

    api_result_file_path_link = f"{folder_input_api_result_link}/{row['API ID']}/{row['Scenario']}.txt"
    return headers, api_result_file_path_link, response_json, response


# def element_input_driver(driver, element_id, input_value):
#     ele_input = WebDriverWait(driver, 10).until(
#         ec.presence_of_element_located((By.ID, element_id))
#     )
#     ele_input.clear()
#     ele_input.send_keys(input_value)
#
#
# def element_button_driver(driver, element_xpath):
#     ele_button = WebDriverWait(driver, 10).until(
#         ec.element_to_be_clickable((By.XPATH, element_xpath))
#     )
#     ele_button.click()


def start():
    sheets_dict = pd.read_excel(file_master_data, sheet_name=None)
    writer = pd.ExcelWriter(file_master_data.replace('.xlsx', ' (Executed).xlsx'), engine="openpyxl")

    # Note: Filter Execution
    # aa api  count: 2
    aa_item = ['API-001', 'API-002']
    # batch api count: 25
    batch_item = ['BAT-001', 'BAT-002', 'BAT-003', 'BAT-017', 'BAT-024',
                  'BAT-025', 'BAT-004', 'BAT-005', 'BAT-008', 'BAT-007',
                  'BAT-009', 'BAT-018', 'BAT-010', 'BAT-019', 'BAT-006',
                  'BAT-012', 'BAT-021', 'BAT-013', 'BAT-022', 'BAT-011',
                  'BAT-020', 'BAT-014', 'BAT-015', 'BAT-023', 'BAT-016']

    #  admin api count: 11
    admin_item = ['API-077', 'API-078', 'API-079', 'API-080',
                  'API-081', 'API-082', 'API-086', 'API-087',
                  'API-083', 'API-084', 'API-085']

    #  common api  count: 62
    common_item_all = ['API-007', 'API-021', 'API-022', 'API-071', 'API-023', 'API-024',
                       'API-026', 'API-072', 'API-027', 'API-028', 'API-029', 'API-063',
                       'API-019', 'API-020', 'API-069', 'API-006', 'API-068', 'API-008',
                       'API-009', 'API-016', 'API-017', 'API-018', 'API-044', 'API-045',
                       'API-074', 'API-046', 'API-047', 'API-048', 'API-041', 'API-042',
                       'API-043', 'API-049', 'API-050', 'API-051', 'API-075', 'API-058',
                       'API-059', 'API-060', 'API-076', 'API-038', 'API-039', 'API-040',
                       'API-052', 'API-053', 'API-054', 'API-055', 'API-056', 'API-057',
                       'API-061', 'API-062', 'API-010', 'API-011', 'API-013', 'API-014',
                       'API-031', 'API-032', 'API-033', 'API-034', 'API-035', 'API-036',
                       'API-003', 'API-004']


    # count: 4
    cusd_account = ["API-006", "API-068", "API-008", "API-009"]
    # count: 4
    enfd_account = ["API-010", "API-011", "API-013", "API-014"]
    # count: 6
    rsd_and_sd_account = ["API-031", "API-032", "API-033", "API-019",
                          "API-020", "API-069"]
    # count: 3
    prd_account = ["API-034", "API-035", "API-036"]

    # count: 45 - 1 = 44
    mpsd_account_opt = set(common_item_all) - set(cusd_account + enfd_account + rsd_and_sd_account +
                                                  prd_account)
    mpsd_account_opt.discard("API-007")
    # run all
    mpsd_account = list(mpsd_account_opt)

    # comment and batch run
    # mpsd_account = [
    #                 'API-024', 'API-028', 'API-058', 'API-041', 'API-074', 'API-039',
    #                 'API-053', 'API-021', 'API-043', 'API-059', 'API-003', 'API-038',
    #                 'API-061', 'API-062', 'API-040', 'API-044', 'API-055', 'API-023',
    #                 'API-047', 'API-048', 'API-051', 'API-054', 'API-027', 'API-060',
    #                 'API-072', 'API-052', 'API-056', 'API-026', 'API-022', 'API-046',
    #                 'API-042', 'API-050', 'API-029', 'API-057', 'API-018', 'API-075',
    #                 'API-004', 'API-045', 'API-071', 'API-017', 'API-049', 'API-016',
    #                 'API-076', 'API-063'
    #                 ]

    # mpsd_account_binary_response_api = ["API-007"] # no need to execute the api

    # single check api
    single_item = ['API-075']

    # all api
    all_set = set(aa_item + batch_item + admin_item + common_item_all)
    all_item = list(all_set)

    # change here
    process_item = mpsd_account

    '''NOTE Deprecated ,coz no autonomy to set trace id in request
        chrome_driver_manager = ChromeDriverManager()
        driver = chrome_driver_manager.get_driver()
    
        driver.get(JAEGER_URL)
        # log in with openshift
        element_button_driver(driver, "/html/body/div/div[2]/form/button")
        # using AD
        element_button_driver(driver, "/html/body/div/div/main/div/ul/li[2]/a")
    
        # input ad account and psw
        element_input_driver(driver, "inputUsername", secret.OCP_LOGIN_NAME)
        element_input_driver(driver, "inputPassword", secret.OCP_LOGIN_PASSWORD)
        element_button_driver(driver, "/html/body/div/div/main/div/form/div[4]/button")
    '''

    for name, sheet in sheets_dict.items():
        if sheet.empty or name == "README" or name == "MASTER":
            continue

        # Filter Execution
        if name not in process_item:
            continue

        print(f"//////////// process {name} //////////// ")
        for index, row in sheet.iterrows():

            if name not in admin_item:
                # coz the refresh_token api belong to  user , not applicable to admin user
                # skip it
                refresh_token()

            trace_id = str(uuid.uuid4())

            # 2. get api result
            print(f"---> execute request < {row['Scenario']} >")
            headers, api_result_file_path_link, response_json, response = extract_api_result_data(row, trace_id)
            print(f"-----------------------------------------\n")

            sheet.at[index, "Request Header"] = json.dumps(headers, indent=4)
            sheet.at[index, "Response File Path"] = api_result_file_path_link
            sheet.at[index, "Response File"] = make_hyperlink(api_result_file_path_link, "API Response")
            sheet.at[index, "Response Body (RAW)"] = json.dumps(response_json, indent=4)
            sheet.at[index, "Response Status"] = response.status_code
            sheet.at[index, "Trace ID"] = trace_id.replace("-", "")

            # Note correct common admin api / aa / batch domain
            # sheet.at[index, "Request API URL"] = row["Request API URL"].replace(
            #     "https://", "https://")

            # Note correct common user api domain
            sheet.at[index, "Request API URL"] = row["Request API URL"].replace(
                "https://", "https://")

            '''NOTE Deprecated,coz no autonomy to set trace id in request
                # 2. get jaeger screenshot
                jaeger_screenshot_path_link = capture_jaeger_screenshot(driver, row, trace_id)
    
                sheet.at[index, "Jaeger Screenshot Path"] = jaeger_screenshot_path_link
                sheet.at[index, "Jaeger Screenshot"] = make_hyperlink(jaeger_screenshot_path_link, "Screenshot")
    
                # 3. get sql statement from jaeger process
                if response.status_code == 200 or response.status_code == 201:
                    # Positive Scenario
                    statement = extract_sql_statement_from_jaeger(driver)
                    sql_statement_file_path_link = construct_sql_statement_file(statement, row)
    
                else:
                    # Negative Scenario
                    # can not extract from jaeger
                    # Note using the same sql statement as Positive Scenario
    
                    folder_sql_statement_path = f"{folder_input_sql_statement}/{row['API ID']}"
                    sql_statement_file_path_link = f"{folder_input_sql_statement_link}/{row['API ID']}/{row['Scenario']}.txt"
    
                    positive_path = f"{folder_sql_statement_path}/Positive Scenario 1.txt"
                    target_negative_path = f"{folder_sql_statement_path}/{row['Scenario']}.txt"
    
                    shutil.copy2(positive_path, target_negative_path)
    
                sheet.at[index, "SQL Path"] = sql_statement_file_path_link
                sheet.at[index, "SQL"] = make_hyperlink(sql_statement_file_path_link, "SQL File")
            '''

        print(f"////////////  finish  {name} ////////////\n\n")

        sheet.to_excel(writer, index=False, sheet_name=name)

    # chrome_driver_manager.close_driver()

    writer.save()
    print(f"============================== done ============================")


if __name__ == '__main__':
    '''
        1. login  portal
        2. copy paste [user_token_download.js] script to chrome console, will auto download token config
        
        <aa,batch,common> api using user token [user_token_download.js]
        <admin> api using admin user token [admin_token_download.js]
    '''
    get_chrome_auto_download_token_file()
    init_local_token()

    start()
    '''
       after success execution
       manually copy and paste sheet content 
       API Test Master Data (Executed).xlsx -> API Test Master Data.xlsx
       
       Note: why not save as origin file API Test Master Data.xlsx ?
       coz if data or exception occur during the process, 
       causing program interruption, 
       will cause origin file damage
    '''
