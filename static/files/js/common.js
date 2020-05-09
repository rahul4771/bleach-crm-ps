// date_pick   
$(function () {
  $('.date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    maxDate: 'now().date()', 
  });
});

