jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

jQuery(document).ready(function($) {
    $(".clickable-row-list").click(function() {
        window.location = $(this).data("href");
    });
});