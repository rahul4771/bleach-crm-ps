$(window).ready(function() {
  
  // active link 
  for (var i = 0; i < document.links.length; i++) {
   if (document.links[i].href == document.URL) {
   $(document.links[i]).parent().addClass('active').append('<div class="active-right"></div>');
 }}
  
});

// date_pick   
$(function () {
  $('.date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    maxDate: 'now().date()', 
  });
});

