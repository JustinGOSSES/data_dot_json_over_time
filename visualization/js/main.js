// Load JSON data and extract specific key values
function getMissingKeyCountData(){
    // JavaScript code to read the variable and render the chart
    const header = document.querySelector('header');
    const path_to_json = header.getAttribute('data-variable');
    console.log("data attribute from header", path_to_json); // Use this variable as needed
    ////
    return fetch(path_to_json) // Return the fetch promise
    .then(response => response.json())
    .then(data => {
        // Use the extracted values
        console.log('data', data);
        console.log('Key1 count:', data['identifiers_in_first_json_missing_from_second_json']['count']);
        return data; // Return the data to the next .then() in the chain
    })
    .catch(error => console.error('Error loading JSON:', error));
}

function updateElementValueById(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = value;
    } else {
        console.error(`Element with ID ${elementId} not found.`);
    }
    console.log("got to here 1")
}

function getCountsPopulate(data){
    console.log("got here 2")
    updateElementValueById('missingKeys_type1', data['identifiers_in_first_json_missing_from_second_json']['count'])
    updateElementValueById('missingKeys_type2', data['identifiers_in_first_json_missing_from_second_json_and_not_same_title_or_close']['count'])
    updateElementValueById('missingKeys_type3', data['identifiers_in_first_json_missing_from_second_json_but_with_same_title']['count'])
    updateElementValueById('missingKeys_type4', data['identifiers_in_first_json_missing_from_second_json_but_with_almost_same_title']['count'])
}

document.addEventListener('DOMContentLoaded', function() {
    getMissingKeyCountData().then(data => {
        console.log("is it doing anything past loading the data at")
        getCountsPopulate(data);
    });
});