$(window).ready(function() {
  
  // active link 
  for (var i = 0; i < document.links.length; i++) {
   if (document.links[i].href == document.URL) {
   $(document.links[i]).parent().addClass('active').first().append('<div class="active-right"></div>');
 }}
  
});

// date_pick   
$(function () {
  $('.date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    //maxDate: 'now().date()', 
  });
});

// date_time_pick   
$(function () {
  $('.date_time_pick').datetimepicker({
    format: "DD/MM/YYYY hh:mm A",
  });
});

 // toggle-password
 $(".toggle-password").click(function() {
  //$(this).toggleClass("fa-eye fa-eye-slash");
  var input = $($(this).attr("toggle"));
  if (input.attr("type") == "password") {
    input.attr("type", "text");
  } else {
    input.attr("type", "password");
  }
  });

// submitAnyForm
function submitAnyForm(src) 
    {
    var form=$(src).parents('form').first();
    if(! form[0].checkValidity())
        $('<input type="submit">').hide().appendTo(form).click().remove();
    else
        {
        $(src).removeAttr('onclick');
        $(src).prop('onclick',null).off('click');
        $(src).text('Submitting...');
        form.submit();
        }
  } 
