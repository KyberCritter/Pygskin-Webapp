// These variables need to be defined here, because there are errors when the Django formatted variables are defined in external JS files
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
