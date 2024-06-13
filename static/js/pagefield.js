document.addEventListener("DOMContentLoaded", function() {
    var wholeDocumentOption = document.getElementById("whole-document");
    var specificRangeOption = document.getElementById("specific-range");
    var pageRangeFields = document.getElementById("page-range-fields");
    var selectionInput = document.getElementById("selection");

    wholeDocumentOption.addEventListener("click", function(event) {
        event.preventDefault();
        selectionInput.value = "whole";
        pageRangeFields.style.display = "none";
    });

    specificRangeOption.addEventListener("click", function(event) {
        event.preventDefault();
        selectionInput.value = "range";
        pageRangeFields.style.display = "block";
    });
});

function showLoading() {
    document.querySelector('.summarize_button').disabled = true;
    document.getElementById('loading').style.display = 'block';
}
