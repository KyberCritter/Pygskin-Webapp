// When the document loads, calculate the number of correct and incorrect predictions to display on the page
document.addEventListener('DOMContentLoaded', function () {
    const correctCells = document.querySelectorAll('.correct');
    const incorrectCells = document.querySelectorAll('.incorrect');

    const correctCount = correctCells.length;
    const incorrectCount = incorrectCells.length;
    const totalCells = correctCount + incorrectCount;

    document.getElementById("prediction-stat").innerHTML = "THE MACHINE LEARNING MODEL CORRECTLY PREDICTED " + correctCount + "/" + totalCells + " PLAYS";
});