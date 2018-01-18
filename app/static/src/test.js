$(document).ready(function() {

    $('#test').on('click', function() {
        console.log($('#email').attr('value'));
        console.log($('#email').html());
        console.log($('#email').val());
    });
});