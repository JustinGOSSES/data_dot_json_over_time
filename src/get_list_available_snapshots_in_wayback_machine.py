#### IMPORTING PYTHON PACKAGES

import json
import yaml
import requests
from datetime import datetime


#### IMPORTING CODE FROM OTHER LOCAL PYTHON FILES

from tools import create_main_data_folder_if_does_not_exist
from tools import save_data_as_json
from tools import fetch_current_data, fetch_current_data_dot_json_from_agency
from tools import snap_shot_availability_for_target_url
from tools import process_snapshot_to_json, call_list_of_dates_fetch_specific_data_dot_json
from tools import process_data_dot_jsonS_to_have_identifier_as_key_as_defined_in_config
from tools import process_json_file_as_defined_in_config
from tools import add_property_to_missing_data_object, compare_jsons_and_calculate_missing_identifiers
from tools import get_status_codes_for_all_urls_in_missing_datasets
from tools import get_status_code, find_most_recent_file_in_folder


#### Get key config variables from config.yml

def get_config():
    with open('../config.yml', 'r') as file:
        config = yaml.safe_load(file)
        return config

config = get_config()
#print("config:",config)
agency_order_in_config = config['agencies'][0]['agency_name_to_run_now']
agency_big_object = config['agencies'][agency_order_in_config]
agency_key_name = list(agency_big_object.keys())[0]
print('agency_key_name ' , agency_key_name)
agency = config['agencies'][agency_order_in_config][agency_key_name]
print("     ")
print("     ")
print("     ")
print("agency",agency)
print("     ")
print("     ")
print("     ")
agency_name = agency['name']
print('agency_name',agency_name)
##
agency_live_data_json_link = agency['agency_live_data_json_link']
print('agency_live_data_json_link :',agency_live_data_json_link)
agency_live_data_json_link = agency['agency_live_data_json_link']
web_archive_cdx_data_for_url_baseUrl = agency['web_archive_cdx_data_for_url_baseUrl']
web_archive_cdx_data_for_url_postfix = agency['web_archive_cdx_data_for_url_postfix']
web_archive_basic_api_url_base = agency['web_archive_basic_api_url_base']
web_archive_basic_api_url_if = agency['web_archive_basic_api_url_if']
## 
dates_to_pull = agency['dates_to_pull']
##
base_agency_path = agency['folder_paths']['base_agency_path']
missing_keys_foldername = agency['folder_paths']['missing_keys_foldername']
snapshots_available_in_archive_foldername = agency['folder_paths']['snapshots_available_in_archive_foldername']
snapshots_available_in_archive_foldername= agency['folder_paths']['snapshots_available_in_archive_foldername']
data_dot_jsons_raw_from_archive_foldername = agency['folder_paths']['data_dot_jsons_raw_from_archive_foldername']
data_dot_jsons_from_agency_page_foldername  = agency['folder_paths']['data_dot_jsons_from_agency_page_foldername']
data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername = agency['folder_paths']['data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername']
data_dot_jsons_cleaned_from_archive_foldername = agency['folder_paths']['data_dot_jsons_cleaned_from_archive_foldername']
data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername = agency['folder_paths']['data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername']


#### Create folder structure if needed that data harvested will go in for one agency data.json
create_main_data_folder_if_does_not_exist(base_agency_path)


### Running code to get snapshot of what is at web archive's WayBack Machine

def get_and_process_snapshots():
    snapshots_raw = snap_shot_availability_for_target_url(web_archive_cdx_data_for_url_baseUrl, web_archive_cdx_data_for_url_postfix, agency_live_data_json_link)
    process_snapshot_to_json(snapshots_raw,base_agency_path,snapshots_available_in_archive_foldername)


get_and_process_snapshots()
