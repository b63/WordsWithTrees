$(document).ready(function () {
    $(".toast").toast({"positionClass": "toast-bottom-full-width"});
    $(".toast").toast('show');
});

// https://stackoverflow.com/questions/21566649/flask-button-run-python-without-refreshing-page
$(function () {
    $('button#close').bind('click', function () {
        var id = $('button#close').data('id');
        var param = 'id=' + id.toString();
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "delete_notification", true);
        //Send the proper header information along with the request
        xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () { // Call a function when the state changes.
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                // Request finished. Do processing here.
            }
        }
        xhttp.send(param);
    });
});