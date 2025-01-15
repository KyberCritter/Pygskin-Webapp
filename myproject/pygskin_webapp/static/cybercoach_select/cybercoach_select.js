// Global object to store drives by year and week
let drivesByYearAndWeek = {};

// Function to group the drives by year and week, taking in the playData, which is an array of drive numbers, and the starting year
function groupDrivesByYearAndWeek(playData, firstYear) {
    let currentYear = firstYear;  // Start with the first year
    let previousWeek = 0;         // Initialize a variable to track the last week processed

    // Iterate over the playData["drive_number"] and playData["week"]
    for (let i = 0; i < playData["drive_number"].length; i++) {
        let week = playData["week"][i];        // Get the current week
        let drive = playData["drive_number"][i]; // Get the drive number

        // If the current week is less than the previous week, increment the year
        if (week < previousWeek) {
            currentYear += 1;
        }

        // Initialize the current year in the drivesByYearAndWeek object if it doesn't exist
        if (!drivesByYearAndWeek[currentYear]) {
            drivesByYearAndWeek[currentYear] = {};
        }

        // Initialize the current week in the current year if it doesn't exist
        if (!drivesByYearAndWeek[currentYear][week]) {
            drivesByYearAndWeek[currentYear][week] = new Set();
        }

        // Add the drive number to the corresponding year and week
        drivesByYearAndWeek[currentYear][week].add(drive);

        // Update previousWeek to the current week for the next iteration
        previousWeek = week;
    }
}

// These are defined in cybercoach_select.html because they are django formatted variables
// const firstYear = {{ first_year }};
// const playData = JSON.parse('{{ play_data|escapejs }}');

groupDrivesByYearAndWeek(playData, firstYear);

// Updates opponent dropdown based on selected year
function updateOpponentDropdown() {
    const yearSelect = document.getElementById('year-select');
    const opponentSelect = document.getElementById('opponent-select');
    const selectedYear = yearSelect.value;

    // Access the embedded JSON data
    const opponentYears = JSON.parse(document.getElementById('opponentYearsData').textContent);
    const opponents = opponentYears[selectedYear];

    // Clear existing options in the opponent dropdown
    while (opponentSelect.firstChild) {
        opponentSelect.removeChild(opponentSelect.firstChild);
    }

    // Populate the opponent dropdown with new options
    for (var i = 0, l = opponents.length; i < l; i++) {
        var opponent = opponents[i][0];
        var week = opponents[i][1];
        const option = document.createElement('option');
        option.value = [opponent, week];
        option.text = opponent.concat(" (Week ", week, ")");
        opponentSelect.appendChild(option);
    }

    const selectedWeek = opponentSelect.value.split(",")[1].trim(); // Get the week from the selected opponent
    updateDriveDropdown(selectedYear, selectedWeek);

    opponentSelect.addEventListener('change', function () {
        const selectedWeek = opponentSelect.value.split(",")[1].trim(); // Get the week from the selected opponent
        updateDriveDropdown(selectedYear, selectedWeek);
    });
}

// Update drive dropdown based on the selected year and week
function updateDriveDropdown(selectedYear, selectedWeek) {
    const driveSelect = document.getElementById('drive-select');

    // Clear existing options in the drive dropdown
    while (driveSelect.firstChild) {
        driveSelect.removeChild(driveSelect.firstChild);
    }

    // Retrieve drives for the selected year and week from the pre-stored data
    const drivesForWeek = drivesByYearAndWeek[selectedYear] && drivesByYearAndWeek[selectedYear][selectedWeek];

    if (drivesForWeek) {
        const uniqueDrives = [...drivesForWeek]; // Convert Set to Array
        for (let drive of uniqueDrives) {
            const option = document.createElement('option');
            option.value = drive;
            option.text = `${drive}`;
            driveSelect.appendChild(option);
        }
    }
}

// When the document loads, run these functions to populate the page correctly based on the coach
document.addEventListener('DOMContentLoaded', function () {
    const cybercoachSelect = document.querySelector('#id_cybercoach');
    if (cybercoachSelect) {
        cybercoachSelect.addEventListener('change', function () {
            const selectedValue = cybercoachSelect.value;
            if (selectedValue && selectedValue !== 'None') {
                document.getElementById('cybercoach-form').submit();
            }
        });
        updateOpponentDropdown();
    }

    // If cybercoach_id is None or invalid, don't proceed
    var cybercoachId = getURLParameter('cybercoach'); // Get 'cybercoach' id from URL
    if (cybercoachId && cybercoachId !== 'None') {
        document.getElementById('cybercoach_id').value = cybercoachId; // Set hidden input
        document.getElementById('cybercoach_id2').value = cybercoachId;
    }
    adjustDownAndDistanceLayout();
});

// Get the URL parameter
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Adjusts the visual layout for the down and distance input fields in the form. Because the forms are generated using Django, this form has to be adjusted after loading, using JavaScript.
function adjustDownAndDistanceLayout() {
    const downInput = document.getElementById('id_down');
    const downLabel = document.querySelector('label[for="id_down"]');

    const distanceInput = document.getElementById('id_distance');
    const distanceLabel = document.querySelector('label[for="id_distance"]');

    downLabel.style.display = 'none';
    distanceLabel.innerHTML = 'AND';
    distanceLabel.style = "margin-top:0px !important;";

    const minsInput = document.getElementById('id_minutes_remaining_in_quarter');
    const minsLabel = document.querySelector('label[for="id_minutes_remaining_in_quarter"]');

    const secsInput = document.getElementById('id_seconds_remaining_in_quarter');
    const secsLabel = document.querySelector('label[for="id_seconds_remaining_in_quarter"]');

    minsLabel.innerHTML = 'TIME REMAINING:';

    if (secsLabel) {
        secsLabel.remove();
    }
    if (minsLabel) {
        minsLabel.remove();
        document.getElementById("will-be-for-time").htmlFor = "id_minutes_remaining_in_quarter";
    }

    document.getElementById("will-be-for-down").htmlFor = "id_down";

    var parentDiv = document.querySelector('.time-remaining');
    var newHeading = document.createElement('h2');
    newHeading.innerHTML = '&nbsp;:&nbsp;';
    var secondInput = document.getElementById('id_seconds_remaining_in_quarter');
    parentDiv.insertBefore(newHeading, secondInput);
}