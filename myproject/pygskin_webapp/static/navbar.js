function openNav() {
    document.getElementById("mySidenav").style.width = "100%";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

document.addEventListener("DOMContentLoaded", function() {
    // This submits the coach_stats when the selected option changes
    const coachSelect = document.querySelector('#select-form');
        if (coachSelect) {
            coachSelect.addEventListener('change', function () {
                document.getElementById('select-form').submit();
            });
        }
});
