// These variables need to be defined here, because there are errors when the django formatted variables are defined in external JS files
// var all_play_dist = [{
//     values: {{ play_dist|safe }},
//     labels: {{ play_types|safe }},
//     marker: { colors: {{ colors|safe }} },
//     type: 'pie'
// }];
// var play_dist_4th = [{
//     values: {{ play_dist_4th_down|safe }},
//     labels: {{ play_types|safe }},
//     marker: { colors: {{ colors|safe }} },
//     type: 'pie'
// }];

var layout = {
    plot_bgcolor: 'rgba(0, 0, 0, 0)',
    paper_bgcolor: 'rgba(0, 0, 0, 0)',
    margin: {
        l: 20,
        r: 20,
        b: 20,
        t: 20
    },
};

document.addEventListener('DOMContentLoaded', function() {
    Plotly.newPlot("playDistChart", all_play_dist, layout);
    Plotly.newPlot("playDist4thDownChart", play_dist_4th, layout);
});