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

//resource date_pick   
$(function () {
  $('.resource_date_pick').datetimepicker({ 
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

//month pick
$('.month_pick').datepicker({
  format: "mm/yyyy",
  startView: "year", 
  minViewMode: "months"
}
);

//New Date picker
   $('.next-day').on('click', function () {

       $selectedDay            = $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").getDate();
       var $tmpSelectedDay     = new Date($selectedDay) 
       $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
       $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
           
    });


   $('.prev-day').on('click', function () {

       $selectedDay            = $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").getDate();
       var $tmpSelectedDay     = new Date($selectedDay) 
       $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
       $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
   
   });

   $('.today-date').on('click', function () {
       var $tmpSelectedDay     = new Date();
       $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
   });


 // toggle-password
 $(".toggle-password").click(function() {
  //$(this).toggleClass("fa-eye fa-eye-slash");
  console.log($(this).prev('input').attr('type'),'ro');
  var input = $(this).prev('input');
  if (input.attr("type") == "password") {
    input.attr("type","text");
    $('.fa').addClass("fa-eye").removeClass("fa-eye-slash");
    console.log(input,"red")
  } else {
    input.attr("type","password");
    $('.fa').addClass("fa-eye-slash").removeClass("fa-eye");
    console.log(input,"rog")
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

// prev next datepicker
$('.datepicker').datetimepicker({ 
  pickTime: false, 
  format: "DD-MM-YYYY",
  defaultDate: new Date(),  
});

  // $('#datepicker').datetimepicker();

 $('.next-day').on('click', function () {

     $selectedDay            = $('#datepicker').data("DateTimePicker").getDate();
     var $tmpSelectedDay     = new Date($selectedDay) 
     $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
     $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
         
  });


 $('.prev-day').on('click', function () {

     $selectedDay            = $('#datepicker').data("DateTimePicker").getDate();
     var $tmpSelectedDay     = new Date($selectedDay) 
     $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
     $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
 
 });

 $('.today-date').on('click', function () {
     var $tmpSelectedDay     = new Date();
     $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
 });

 //filter popup toggle
 $(".arrow").on('click', function (e) {
  $(".arrow").toggleClass("cross");
  $(".menu-filter").slideToggle("");
});

$(".arrow-left").on('click', function (e) {
  $(".arrow-left").toggleClass("cross-left");
  $(".menu-filter-left").slideToggle("");
});

// toggle month/date resources
$('#daymonthtoggle_resource').click(function(){
  if($(this).is(':checked')){
      $('#resource_month').attr("hidden",false);
      $('#working_calendar').attr("hidden",true);
      $('#table_month').attr("hidden",false);
      $('#table_date').attr("hidden",true);
      $('.togglehide').attr("hidden",true);
      $('.red-btn').attr("hidden",true);
      $('.red-btn2').attr("hidden",false);
      $('#resource_search').attr("hidden",true);
      $('#resource_search2').attr("hidden",false);
      load_workers_data();
  }else{
      $('#resource_month').attr("hidden",true);
      $('#working_calendar').attr("hidden",false);
      $('#table_month').attr("hidden",true);
      $('#table_date').attr("hidden",false);
      $('.togglehide').attr("hidden",false);
      $('.red-btn').attr("hidden",false);
      $('.red-btn2').attr("hidden",true);
      $('#resource_search').attr("hidden",false);
      $('#resource_search2').attr("hidden",true);
  }
});

