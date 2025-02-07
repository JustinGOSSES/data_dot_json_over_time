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
print("agency",agency)
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


#### Run code to fetch all dates in config.yml for given agency if not already in folder

def collection_and_process_all_data_defined_in_config(agency_live_data_json_link, web_archive_basic_api_url_base,web_archive_basic_api_url_if,dates_to_pull_list,base_agency_path,data_dot_jsons_raw_from_archive_foldername):
    # fetch needed raw data as defined in config
    print('calling fetch_current_data_dot_json_from_agency() function')
    fetch_current_data_dot_json_from_agency(agency_live_data_json_link, base_agency_path,data_dot_jsons_from_agency_page_foldername)
    #
    #call_list_of_dates_fetch_specific_data_dot_json()
    print('calling call_list_of_dates_fetch_specific_data_dot_json() function')

    call_list_of_dates_fetch_specific_data_dot_json(agency_live_data_json_link, web_archive_basic_api_url_base,web_archive_basic_api_url_if,dates_to_pull_list,base_agency_path,data_dot_jsons_raw_from_archive_foldername) 
    # process raw data files from archive
    print("calling process_json_file_as_defined_in_config() function")
    process_json_file_as_defined_in_config(base_agency_path, data_dot_jsons_raw_from_archive_foldername,data_dot_jsons_cleaned_from_archive_foldername, dates_to_pull)
    # add identifier as object key to make processing faster (files from archive)
    # add identifier as object key to make processing faster (files from live agency grabs)
    print('calling function to create new JSONs with identifiers as keys')
    process_data_dot_jsonS_to_have_identifier_as_key_as_defined_in_config(agency, base_agency_path, data_dot_jsons_cleaned_from_archive_foldername,data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername,data_dot_jsons_from_agency_page_foldername,dates_to_pull,data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername)
    # compare data and generate metrics
    
collection_and_process_all_data_defined_in_config(agency_live_data_json_link, web_archive_basic_api_url_base,web_archive_basic_api_url_if,dates_to_pull,base_agency_path,data_dot_jsons_raw_from_archive_foldername)


#### Find most recent agency live data.json in folder of them
print("got to part of code that finds the right data dot jsons to use if nothing else provided")

most_recent_file_from_live_agency_data_dot_json_url_path = find_most_recent_file_in_folder(base_agency_path, data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername)
print('most_recent_file_from_live_agency_data_dot_json_url_path = ',most_recent_file_from_live_agency_data_dot_json_url_path)
#### Find last known Biden administration data.json archive snapshot

most_recent_file_from_web_archive_snapshot_from_biden_administration_path = find_most_recent_file_in_folder(base_agency_path, data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername, but_not_more_recent_than='20250119')
print('most_recent_file_from_web_archive_snapshot_from_biden_administration_path  = ',most_recent_file_from_web_archive_snapshot_from_biden_administration_path )
#### compare_jsons_and_calculate_missing_identifiers() function
#### compare either all known data.jsons or
#### user provided dates & type...
#### .....to allow for comparison of directly harvested JSONs at times web archive doesn't have

print('got to start of comparison code that finds missing identifiers between data dot jsons')
missing_data_object, first_snapshot_date, second_snapshot_date, missing_identifiers_folder  = compare_jsons_and_calculate_missing_identifiers(most_recent_file_from_live_agency_data_dot_json_url_path, most_recent_file_from_web_archive_snapshot_from_biden_administration_path, missing_keys_foldername,base_agency_path)

print('got to start of 2nd function of comparison code that finds missing identifiers between data dot jsons')
missing_data_object = get_status_codes_for_all_urls_in_missing_datasets(missing_data_object, first_snapshot_date, second_snapshot_date, missing_identifiers_folder, base_agency_path)
