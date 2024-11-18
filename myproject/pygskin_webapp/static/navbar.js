    function openNav() {
        document.getElementById("mySidenav").style.width = "100%";
    }

    function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
    }

    // THIS JAVASCRIPT IS TO FIX THE FOOTER ISSUE ON COACH_STATS WHEN THERE IS NO COACH SELECTED
    document.addEventListener("DOMContentLoaded", function() {
        const url = window.location.href;
        const exactPath = /\/coach_stats\/$/; // Matches exactly "/coach_stats/"
        const pathWithCoachParam = /\/coach_stats\/\?coach=$/; // Matches exactly "/coach_stats/?coach="

        if (exactPath.test(url) || pathWithCoachParam.test(url)) {
            const containers = document.getElementsByClassName('container');
            for (let container of containers) {
                container.style.padding = '0px';
            }
        }
        else {
            const containers = document.getElementsByClassName('container');
            for (let container of containers) {
                container.style.padding = '20px 7vw';
            }
        }

        // THIS IS TO MAKE THE COACH STATS SELECT FORM WORK
        const coachSelect = document.querySelector('#select-form');
            if (coachSelect) {
               coachSelect.addEventListener('change', function () {
                   document.getElementById('select-form').submit();
               });
            }
    });