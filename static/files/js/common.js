$(window).ready(function() {
  
  // active link 
  for (var i = 0; i < document.links.length; i++) {
    if (document.links[i].href == document.URL) {
                $(document.links[i]).parent().addClass('active').first().append('<div class="active-right"></div>');
                                            } 
                              }
});


// date_pick   
$(function () {
  $('.date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    //maxDate: 'now().date()', 
  });
});

//time pick
//tendative time initial
$(function () {
  $(".time_pick").datetimepicker({
    pickDate:false,
    format: 'hh:mm A',
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

// add-field and remove
$('.multi_field_wrapper').each(function() {
  var $wrapper = $('.multi-fields', this); 
  $(".add-field-btn", $(this)).click(function(e) {
    var filed = $('.multi-field:first-child', $wrapper).clone(true);
      filed.appendTo($wrapper).find('textarea').val('')
      filed.appendTo($wrapper).find('input').val('').focus()
      filed.appendTo($wrapper).find('img').val('').focus().prop('src', "/static/files/images/default-img.png");
});
  $('.multi-field .remove-field-btn', $wrapper).click(function() {
      if ($('.multi-field', $wrapper).length > 1)
          $(this).parent('.multi-field').remove();
  });
});



// filter
$(document).ready(function() {

$(".params_filter .filter-btn").on("click", function(){
    $(this).parent(".params_filter").toggleClass("active");
    console.log("hiii");
});
$(".close-btn").on("click", function(){
    $('.params_filter').removeClass('active');
});

});

