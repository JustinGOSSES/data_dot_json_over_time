import json
import yaml
import requests
from datetime import datetime
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_main_data_folder_if_does_not_exist(base_agency_path):
    if not os.path.exists(base_agency_path):
        os.makedirs(base_agency_path)

def save_data_as_json(data, filename):
    print("attempting to save file: ",filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print('saved file: ',filename)
            
def find_first_file_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if files:
            return files[0]
    return None

def find_most_recent_file_in_folder(base_path, folder_path, but_not_more_recent_than=None):
    most_recent_file = None
    most_recent_timestamp = None
    filenames = []
    full_folder_path = base_path + folder_path
    print('full_folder_path:', full_folder_path )
    for (root, dirs, files) in os.walk(full_folder_path ):
        filenames.extend(files)
    print("filenames ",filenames)
    for file in filenames:
        try:
            print(f"File: {file}")
            timestamp = datetime.strptime(file.replace('.json', ''), '%Y%m%d%H%M%S')
            if (most_recent_timestamp is None or timestamp > most_recent_timestamp) and (but_not_more_recent_than is None or timestamp <= datetime.strptime(but_not_more_recent_than, '%Y%m%d')):
                most_recent_timestamp = timestamp
                most_recent_file = file
        except ValueError:
            continue
    print('base_path',base_path)
    print('folder_path = ',folder_path)
    print("3: most_recent_file = ",most_recent_file)
    full_file_path = os.path.join(base_path, folder_path, most_recent_file)
    return full_file_path

def find_least_recent_file_in_folder(base_path, folder_path):
    least_recent_file = None
    least_recent_timestamp = None
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                timestamp = datetime.strptime(file.replace('.json', ''), '%Y%m%d%H%M%S')
                if least_recent_timestamp is None or timestamp < least_recent_timestamp:
                    least_recent_timestamp = timestamp
                    least_recent_file = file
            except ValueError:
                continue
    full_file_path = base_path + folder_path + east_recent_file
    return full_file_path
            
def fetch_current_data(target_url):
    response = requests.get(target_url)
    data = response.json()
    return data

def fetch_all_configuration():
    with open('../config.yml', 'r') as file:
        config = yaml.safe_load(file)

    agency = config['agencies']['agency_name_to_run_now']
    agency_live_data_json_link = config['agencies'][agency]['agency_live_data_json_link']
    web_archive_cdx_data_for_url_baseUrl = config['agencies'][agency]['web_archive_cdx_data_for_url_baseUrl']
    web_archive_cdx_data_for_url_postfix = config['agencies'][agency]['web_archive_cdx_data_for_url_postfix']

    base_agency_path = config['agencies'][agency]['base_agency_path']
    snapshots_available_in_archive_foldername = config['agencies'][agency]['snapshots_available_in_archive_foldername']
    data_dot_jsons_from_agency_page_foldername  = config['agencies'][agency]['data_dot_jsons_from_agency_page_foldername']

    dates_to_pull_list = config['agencies'][agency]['dates_to_pull']
    
    return config, agency, agency_live_data_json_link, web_archive_cdx_data_for_url_baseUrl, web_archive_cdx_data_for_url_postfix, base_agency_path, snapshots_available_in_archive_foldername, data_dot_jsons_from_agency_page_foldername, dates_to_pull

def snap_shot_availability_for_target_url(web_archive_cdx_data_for_url_baseUrl, web_archive_cdx_data_for_url_postfix, agency_live_data_json_link):
    # web_archive_cdx_data_for_url_baseUrl = 'https://web.archive.org/cdx/search/cdx?url='
    # web_archive_cdx_data_for_url_postfix = '&output=json'
    combined_url = web_archive_cdx_data_for_url_baseUrl + agency_live_data_json_link  + web_archive_cdx_data_for_url_postfix
    url = combined_url
    response = requests.get(url)
    print("response: ", response)
    print("response type: ", type(response))
    data = response.json()
    print("type data",type(data))
    return data

def process_snapshot_to_json(snapshots_raw,base_agency_path,snapshots_available_in_archive_foldername):
    # Define the keys
    keys = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
    # Extract the list of snapshots from the response data
    snapshots_list = snapshots_raw[1:]  # The first element is the header
    #snapshots_list = snapshots_raw
    # Process the list into a JSON with the specified keys
    print('snapshots_list',snapshots_list)
    new_object_list = []
    processed_snapshots = [dict(zip(keys, snapshots_raw)) for snapshot in snapshots_list]
    for snapshot in snapshots_list:
        new_snap_object = {}
        for key in [0,1,2,3,4,5,6]:
            new_snap_object[keys[key]] = snapshot[key]
        new_object_list.append(new_snap_object)
            
    # Get time
    timestamp_now = datetime.now().strftime('%Y%m%d%H%M%S')
    # Save JSON of snapshots
    folder_for_data = base_agency_path
    data_file_path = folder_for_data + snapshots_available_in_archive_foldername  + timestamp_now  + '.json'   
    save_data_as_json(new_object_list , data_file_path)
    print("saved processed snapshot data to file path: ",data_file_path)
    
def get_and_process_snapshots(web_archive_cdx_data_for_url_baseUrl, web_archive_cdx_data_for_url_postfix, agency_live_data_json_link,snapshots_raw,base_agency_path,snapshots_available_in_archive_foldername):
    snapshots_raw = snap_shot_availability_for_target_url(web_archive_cdx_data_for_url_baseUrl, web_archive_cdx_data_for_url_postfix, agency_live_data_json_link)
    process_snapshot_to_json(snapshots_raw,base_agency_path,snapshots_available_in_archive_foldername)

def fetch_current_data_dot_json_from_agency(agency_live_data_json_link, base_agency_path,data_dot_jsons_from_agency_page_foldername):
    #### Get timestampe
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    #### Create file path for where to put data.json harvested from live site
    data_file_path = base_agency_path + data_dot_jsons_from_agency_page_foldername + timestamp + '.json'   
    #### Fetch live data.json and save it in the proper directory
    save_data_as_json(fetch_current_data(agency_live_data_json_link ),data_file_path)

def fetch_specific_data_dot_json(target_url, date_version, base_url, base_url_if):
    url = base_url + date_version + base_url_if + target_url
    response = requests.get(url)
    data = response.json()
    return data

def call_list_of_dates_fetch_specific_data_dot_json(agency_live_data_json_link, web_archive_basic_api_url_base,web_archive_basic_api_url_if,dates_to_pull_list,base_agency_path,data_dot_jsons_raw_from_archive_foldername ):
    # with open('../config.yml', 'r') as file:
    #     config = yaml.safe_load(file)
    # agency = config['agencies']['agency_name_to_run_now']
    # #
    # web_archive_basic_api_url_base = config['agencies'][agency]['web_archive_basic_api_url_base']
    # web_archive_basic_api_url_if = config['agencies'][agency]['web_archive_basic_api_url_if']
    # dates_to_pull_list = config['agencies'][agency]['dates_to_pull']
    # #
    # base_agency_path = config['agencies'][agency]['base_agency_path']
    # data_dot_jsons_raw_from_archive_foldername = config['agencies'][agency]['data_dot_jsons_raw_from_archive_foldername']
    # Get time
    timestamp_now = datetime.now().strftime('%Y%m%d%H%M%S')
    # Create part of file path
    folder_for_data = base_agency_path + data_dot_jsons_raw_from_archive_foldername
    # For each timestamp needed
    for time_of_snapshot in dates_to_pull_list:
        # Create file path 
        data_file_path = folder_for_data + time_of_snapshot + '.json'
        # Check if timestamp already exists in folder
        if not os.path.exists(data_file_path):
            data = fetch_specific_data_dot_json(agency_live_data_json_link, time_of_snapshot, web_archive_basic_api_url_base, web_archive_basic_api_url_if)
            save_data_as_json(data, data_file_path) 
    
def process_json_file(input_file_path, output_file_path,date_of_file):
    ## For the wayback machine links to work, it injects its own base URL
    ## Into any existing URLs. For our purposes we need to process that out. 
    old_string = 'https://web.archive.org/web/'+date_of_file+'/'
    new_string = ''
    input_file_no_path = date_of_file + '.json'
    output_file_no_path = date_of_file + '.json'
    # Full path
    # input_file_path = input_folder_path_no_file + input_file_no_path 
    # output_file_path = outout_folder_path_no_file + output_file_no_path
    ##
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(input_file_path, 'r') as f:
        file_content = f.read()
    #
    updated_file_content = file_content.replace(old_string, new_string)
    json_data = json.loads(updated_file_content)
    #
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, 'w') as f:
        json.dump(json_data, f, indent=4)
    return json_data


def process_json_file_as_defined_in_config(base_agency_path,input_folder_path, output_folder_path,dates_to_pull_list):
    ### THIS PROCESSING ONLY NECESSARY FOR DATA DOT JSON FROM WAYBACK MACHINE
    list_of_output_filepaths_that_should_exist_eventually = []
    for time_of_snapshot in dates_to_pull_list:
        list_of_output_filepaths_that_should_exist_eventually.append(output_folder_path+time_of_snapshot+'.json')
    ## Check if file exists in output, if it does, pass
    for date_of_file in dates_to_pull_list:
        input_file_path = base_agency_path + input_folder_path + date_of_file + '.json'
        output_file_path = base_agency_path + output_folder_path + date_of_file + '.json'
        if os.path.exists(output_file_path):
            print(f"Output file {output_file_path} already exists. Skipping processing.")
        ## if output file does not exist, create it
        else: 
            process_json_file(input_file_path, output_file_path, date_of_file)
    
def process_data_dot_json_to_have_identifier_as_key(input_file_path, output_file_path):
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(input_file_path, 'r') as f:
        file_content = f.read()
    
    data = json.loads(file_content)
    list_of_datasets = data['dataset']

    new_data = {}
    for dataset in list_of_datasets:
        identifier = dataset['identifier']
        new_data[identifier] = dataset

    data['dataset'] = new_data

    ## write data to file
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    print("in function process_data_dot_json_to_have_identifier_as_key and output_file_path = ",output_file_path)
    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=4)
    return data

def process_data_dot_jsonS_to_have_identifier_as_key_as_defined_in_config(agency, base_agency_path, data_dot_jsons_cleaned_from_archive_foldername,data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername,data_dot_jsons_from_agency_page_foldername,dates_to_pull,data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername):
    # for data dot jsons from wayback machine archive
    input_folder_path = data_dot_jsons_cleaned_from_archive_foldername ###= base_agency_path = config['agencies'][agency]['base_agency_path'] + config['agencies'][agency]['data_dot_jsons_cleaned_from_archive_foldername']
    output_folder_path = data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername# = base_agency_path = config['agencies'][agency]['base_agency_path'] + config['agencies'][agency]['data_dot_jsons_cleaned_from_archive_ObjectNotList_foldername']
    dates_to_pull_list = dates_to_pull #config['agencies'][agency]['dates_to_pull']
    # for each date 
    for date_of_file in dates_to_pull_list:
        input_file_path = base_agency_path + input_folder_path + date_of_file + '.json'
        output_file_path = base_agency_path + output_folder_path + date_of_file + '.json'
        if os.path.exists(output_file_path):
            print(f"Output file {output_file_path} already exists. Skipping processing.") 
        else: ## if output file does not exist, create it
            print("in process_data_dot_jsonS_to_have_identifier_as_key_as_defined_in_config calling process_data_dot_json_to_have_identifier_as_key() function with output_file_path of : ",output_file_path)
            data = process_data_dot_json_to_have_identifier_as_key(input_file_path, output_file_path)
    # for latest live version from agency URl for data.json
    input_folder_path = base_agency_path + data_dot_jsons_from_agency_page_foldername #= config['agencies'][agency]['base_agency_path'] + config['agencies'][agency]['data_dot_jsons_from_agency_page_foldername']
    output_folder_path = base_agency_path + data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername #= # config['agencies'][agency]['base_agency_path'] + config['agencies'][agency]['data_dot_jsons_cleaned_from_agency_page_ObjectNotList_foldername']
    first_file_name_in_folder = find_first_file_in_folder(input_folder_path)
    first_file_name_in_folder = first_file_name_in_folder.replace('.json','')
    input_file_path = input_folder_path + first_file_name_in_folder + '.json'
    output_file_path = output_folder_path + '/' + first_file_name_in_folder + '.json'
    #
    if os.path.exists(output_file_path):
            print(f"Output file {output_file_path} already exists. Skipping processing.") 
    else: 
        ## if output file does not exist, create it
        print("in 2nd part of process_data_dot_jsonS_to_have_identifier_as_key_as_defined_in_config calling process_data_dot_json_to_have_identifier_as_key() function with output_file_path of : ",output_file_path)
        data = process_data_dot_json_to_have_identifier_as_key(input_file_path, output_file_path)
    

#### This function is used with function compare_jsons_and_calculate_missing_identifiers
def add_property_to_missing_data_object(list_identifiers, list_name, missing_data_object,json1):
    missing_data_object[list_name] = {
        "count": len(list_identifiers),
        "list": list_identifiers,
        "object": {key: json1['dataset'][key] for key in list_identifiers}
    }
    return missing_data_object


####
#### 
def compare_jsons_and_calculate_missing_identifiers(first_data_dot_json_cleaned_structured_full_path, second_data_dot_json_cleaned_structured_full_path, missing_identifiers_folder,base_agency_path):
    # Read JSON files
    with open(first_data_dot_json_cleaned_structured_full_path, 'r') as f:
        json1 = json.load(f)

    with open(second_data_dot_json_cleaned_structured_full_path, 'r') as f:
        json2 = json.load(f)
    
    first_snapshot_date = first_data_dot_json_cleaned_structured_full_path.split('/')[-1].replace('.json','')
    second_snapshot_date = second_data_dot_json_cleaned_structured_full_path.split('/')[-1].replace('.json','')
    
    identifiers_in_first_json_missing_from_second_json = []

    for key in json1['dataset'].keys():
        if key not in json2['dataset']:
            identifiers_in_first_json_missing_from_second_json.append(key)
            
    identifiers_in_first_json_missing_from_second_json_but_with_same_title = []
    identifiers_in_first_json_missing_from_second_json_and_not_same_title = []
    identifiers_in_first_json_missing_from_second_json_but_with_almost_same_title = []

    json2_keys = list(json2['dataset'].keys())

    for key in identifiers_in_first_json_missing_from_second_json:
        dataset_missing_w_missing_id = json1['dataset'][key]
        title = dataset_missing_w_missing_id['title']
        for key2 in json2_keys:
            if json2['dataset'][key2]['title'] == title:
                identifiers_in_first_json_missing_from_second_json_but_with_same_title.append(key)
                break
            else:
                if key in identifiers_in_first_json_missing_from_second_json_and_not_same_title:
                    pass
                else:
                    identifiers_in_first_json_missing_from_second_json_and_not_same_title.append(key)
                    title_parts = re.split(r'[_\-. ]|ver', title)
                    json2_title_parts = re.split(r'[_\-. ]|ver', json2['dataset'][key2]['title'])
                    if title_parts[:-1] == json2_title_parts[:-1]:
                        identifiers_in_first_json_missing_from_second_json_but_with_almost_same_title.append(key)
    
    missing_data_object = {}
    add_property_to_missing_data_object(identifiers_in_first_json_missing_from_second_json, 'identifiers_in_first_json_missing_from_second_json', missing_data_object,json1)
    add_property_to_missing_data_object(identifiers_in_first_json_missing_from_second_json_and_not_same_title, 'identifiers_in_first_json_missing_from_second_json_and_not_same_title', missing_data_object,json1)
    add_property_to_missing_data_object(identifiers_in_first_json_missing_from_second_json_but_with_same_title, 'identifiers_in_first_json_missing_from_second_json_but_with_same_title', missing_data_object,json1)
    add_property_to_missing_data_object(identifiers_in_first_json_missing_from_second_json_but_with_almost_same_title, 'identifiers_in_first_json_missing_from_second_json_but_with_almost_same_title', missing_data_object,json1)
    
    missing_identifiers_filename = first_snapshot_date + "_vs_" + second_snapshot_date + "_missingKeysInSecondNoTitleMatch" + ".json"
    missing_identifiers_path = base_agency_path + missing_identifiers_folder + missing_identifiers_filename
    save_data_as_json(missing_data_object, missing_identifiers_path)
    
    return missing_data_object, first_snapshot_date, second_snapshot_date, missing_identifiers_folder


def get_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    

def get_status_codes_for_all_urls_in_missing_datasets(missing_data_object, first_snapshot_date, second_snapshot_date, missing_identifiers_folder,base_agency_path):
    current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    object_of_urls_with_status_results = {}

    def check_url_status(url):
        if url in object_of_urls_with_status_results:
            return url, object_of_urls_with_status_results[url]
        else:
            status_code = get_status_code(url)
            object_of_urls_with_status_results[url] = status_code
            return url, status_code

    urls_to_check = []

    for missing_data_type in missing_data_object:
        for identifier in missing_data_object[missing_data_type]['list']:
            missing_data_object[missing_data_type]['object'][identifier]['url_status_checks'] = {}
            landing_page_url = missing_data_object[missing_data_type]['object'][identifier].get('landingPage', None)
            if landing_page_url:
                urls_to_check.append(landing_page_url)
            for distribution in missing_data_object[missing_data_type]['object'][identifier]['distribution']:
                downloadURL = distribution['downloadURL']
                if downloadURL:
                    urls_to_check.append(downloadURL)
        print("got to end of identifiers for this type of missing: ",missing_data_type)
    urls_to_check = list(set(urls_to_check))
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url_status, url): url for url in urls_to_check}
        for future in as_completed(future_to_url):
            url, status_code = future.result()
            for missing_data_type in missing_data_object:
                for identifier in missing_data_object[missing_data_type]['list']:
                    print("starting http status checks for pages for identifier: ", identifier)
                    if missing_data_object[missing_data_type]['object'][identifier].get('landingPage') == url:
                        if 'url_status_checks' not in missing_data_object[missing_data_type]['object'][identifier]:
                            missing_data_object[missing_data_type]['object'][identifier]['url_status_checks'] = {}
                        missing_data_object[missing_data_type]['object'][identifier]['url_status_checks']['landingPage'] = {url: {current_timestamp: status_code}}
                    for distribution in missing_data_object[missing_data_type]['object'][identifier]['distribution']:
                        if 'url_status_checks' not in missing_data_object[missing_data_type]['object'][identifier]:
                            missing_data_object[missing_data_type]['object'][identifier]['url_status_checks'] = {}
                        if 'distributions_downloadURLs' not in missing_data_object[missing_data_type]['object'][identifier]['url_status_checks']:
                            missing_data_object[missing_data_type]['object'][identifier]['url_status_checks']['distributions_downloadURLs'] = {}
                        if distribution['downloadURL'] == url:
                            missing_data_object[missing_data_type]['object'][identifier]['url_status_checks']['distributions_downloadURLs'][url] = {current_timestamp: status_code}

    missing_identifiers_filename = first_snapshot_date + "_vs_" + second_snapshot_date + "_missingKeysInSecondNoTitleMatch_WebStatusChecks" + ".json"
    missing_identifiers_path = base_agency_path + missing_identifiers_folder + missing_identifiers_filename
    save_data_as_json(missing_data_object, missing_identifiers_path)
    print('got to end')
    return missing_data_object

