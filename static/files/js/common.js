$(window).ready(function() {
  
  // active link 
  for (var i = 0; i < document.links.length; i++) {
    
    lastchar_of_currentlink= (document.URL).slice(-1)
    if(lastchar_of_currentlink == '#')
      {
        current_link = (document.URL).slice(0,-1);
      }
    else{
        current_link = document.URL
    }  
    
    if (document.links[i].href == current_link) {
                $(document.links[i]).parent().addClass('active').first().append('<div class="active-right"></div>');
                                            } 
                              }
});

//Image Validation
$('input[type="file"]').change(function() {
        var val = $(this).val();
        $('.image_validation_msg').remove(); 
        if(this.files[0].size>110000000)
        {
          alert("Upto 100MB File Upload is Possible");
        }

        switch(val.substring(val.lastIndexOf('.') + 1).toLowerCase()){
            case 'gif': case 'jpg': case 'png': case 'jpeg': case 'bmp':
                break;
            default:
                $(this).val('');
                // error message here
                alert("Only JPG,PNG,BMP and JPEG supported");
                break;
        }
});

//date_pick   
$(function () {
  $('.date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    //maxDate: 'now().date()', 
  });
});

$(function () {
  var today = new Date();
  $('.date_pick_chart_from').datetimepicker({
      pickTime: false, 
      format: 'DD-MM-YYYY',
      autoclose:true,
      endDate: "today",
      maxDate: today,
  }).on('changeDate', function (ev) {
          $(this).datetimepicker('hide');
      });
});

$(function () {
  var today = new Date();
  $('.date_pick_chart_to').datetimepicker({
      pickTime: false, 
      format: 'DD-MM-YYYY',
      autoclose:true,
      endDate: "today",
      maxDate: today,
  }).on('changeDate', function (ev) {
          $(this).datetimepicker('hide');
      });
});

//date validation in charts
function fromtodatecheck() {
  var d1 = $('.date_pick_chart_from').val();

  var vals = d1.split('-');
  var day = parseInt(vals[0]);
  var month = parseInt (vals[1]);
  var year = parseInt (vals[2]);

  var d1date = new Date(year,month,day);
  d1date.setMonth(d1date.getMonth()-1);
  
  var d2 = $('.date_pick_chart_to').val();

  var vals2 = d2.split('-');
  var day2 = parseInt(vals2[0]);
  var month2 = parseInt (vals2[1]);
  var year2 = parseInt (vals2[2]);

  var d2date = new Date(year2,month2,day2);
  d2date.setMonth(d2date.getMonth()-1);

  console.log(d1,d2,"dee")
  if ( d1date > d2date){
    $('.date_pick_chart_from').val(d2);
    $('.date_pick_chart_to').val(d1);
  }
};

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
$('.month_pick').datetimepicker({
  maxDate: new Date(),
  pickTime: false,
  format: "MM/YYYY",
  startView: "year", 
  minViewMode: "months",
  autoclose:true,
}).on('changeDate', function (ev) {
  $(this).datetimepicker('hide');
});

$('.month_pick_resource').datetimepicker({
  pickTime: false,
  format: "MM/YYYY",
  startView: "year", 
  minViewMode: "months",
  autoclose:true,
}).on('changeDate', function (ev) {
  $(this).datetimepicker('hide');
});

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


//resource date_pick   
$(function () {
  $('.resource_date_pick').datetimepicker({ 
    pickTime: false, 
    format: "DD-MM-YYYY", 
    //maxDate: 'now().date()', 
  });
});

//New Date picker
  $('.next-day-resource').on('click', function () {

    console.log($(this).parent('.date-wrapper-inner-resource'));
    $selectedDay            = $(this).parent('#working_calendar').children('.resource_date_pick').data("DateTimePicker").getDate();
    var $tmpSelectedDay     = new Date($selectedDay) 
    $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
    $(this).parent('#working_calendar').children('.resource_date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
        
  });



   $('.prev-day-resource').on('click', function () {

       $selectedDay            = $(this).parent('#working_calendar').children('.resource_date_pick').data("DateTimePicker").getDate();
       var $tmpSelectedDay     = new Date($selectedDay) 
       $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
       $(this).parent('#working_calendar').children('.resource_date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
   
   });

   $('.today-date-resource').on('click', function () {
       var $tmpSelectedDay     = new Date();
       $(this).parent('#working_calendar').children('.resource_date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
   });   


//New Month picker
$('.next-month-resource').on('click', function () {

  console.log($(this).parent('.date-wrapper-inner-resource'));
  $selectedDay            = $(this).parent('#working_calendar2').children('.month_pick_resource').data("DateTimePicker").getDate();
  var $tmpSelectedDay     = new Date($selectedDay) 
  $tmpSelectedDay.setMonth($tmpSelectedDay.getMonth() + 1);
  $(this).parent('#working_calendar2').children('.month_pick_resource').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('MM/YYYY'));;
      
});

$('.prev-month-resource').on('click', function () {

  $selectedDay            = $(this).parent('#working_calendar2').children('.month_pick_resource').data("DateTimePicker").getDate();
  var $tmpSelectedDay     = new Date($selectedDay) 
  $tmpSelectedDay.setMonth($tmpSelectedDay.getMonth() - 1);
  $(this).parent('#working_calendar2').children('.month_pick_resource').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('MM/YYYY'));

});

$('.this-month-resource').on('click', function () {
  var $tmpSelectedDay     = new Date();
  $tmpSelectedDay.setMonth($tmpSelectedDay.getMonth());
  $(this).parent('#working_calendar2').children('.month_pick_resource').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('MM/YYYY'));
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
    console.log(form);
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
    console.log("hellooo")
});

});

// prev next datepicker
// $('.datepicker').datetimepicker({ 
//   pickTime: false, 
//   format: "DD-MM-YYYY",
//   defaultDate: new Date(),  
// });

  // $('#datepicker').datetimepicker();

//  $('.next-day').on('click', function () {
//      $selectedDay            = $('#datepicker').data("DateTimePicker").getDate();
//      var $tmpSelectedDay     = new Date($selectedDay) 
//      $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
//      $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
         
//   });


//  $('.prev-day').on('click', function () {

//      $selectedDay            = $('#datepicker').data("DateTimePicker").getDate();
//      var $tmpSelectedDay     = new Date($selectedDay) 
//      $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
//      $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
 
//  });

//  $('.today-date').on('click', function () {
//      var $tmpSelectedDay     = new Date();
//      $('#datepicker').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
//  });

 //filter popup toggle
 $(".arrow").on('click', function (e) {
  $(".arrow").toggleClass("cross");
  $(".menu-filter").slideToggle("");
});

$(".arrow-close").on('click', function (e) {
  
  //clear all
  $(".menu-filter").find(':input').each(function() {
    switch(this.type) {
        case 'password':
        case 'text':
        case 'textarea':
        case 'file':
        case 'select-one':
        case 'select-multiple':
        case 'date':
        case 'number':
        case 'tel':
        case 'email':
            $(this).val('');
            break;
        case 'checkbox':
        case 'radio':
            this.checked = false;
            break;
    }
  });

});



$(".arrow-left").on('click', function (e) {
  console.log("plo")
  $(".arrow-left").toggleClass("cross-left");
  $(".menu-filter-left").slideToggle("");
});

$(".red-btn2").on('click', function (e) {
  $(".arrow-left").toggleClass("cross-left");
  $(".menu-filter-left").slideToggle("");
});

$(".arrow-left-close").on('click', function (e) {  
  //clear all
  $(".menu-filter-left").find(':input').each(function() {
    switch(this.type) {
        case 'password':
        case 'text':
        case 'textarea':
        case 'file':
        case 'select-one':
        case 'select-multiple':
        case 'date':
        case 'number':
        case 'tel':
        case 'email':
            $(this).val('');
            break;
        case 'checkbox':
        case 'radio':
            this.checked = false;
            break;
    }
  });

});

// toggle month/date resources
// $('#daymonthtoggle_resource').click(function(){
//   if($(this).is(':checked')){
//       $('#working_calendar2').attr("hidden",false);
//       $('#working_calendar').attr("hidden",true);
//       $('#table_month').attr("hidden",false);
//       $('#table_date').attr("hidden",true);
//       $('.togglehide').attr("hidden",true);
//       $('.red-btn').attr("hidden",true);
//       $('.red-btn2').attr("hidden",false);
//       $('#resource_search').attr("hidden",true);
//       $('#resource_search2').attr("hidden",false);
//       load_workers_data();
//   }else{
//       $('#working_calendar2').attr("hidden",true);
//       $('#working_calendar').attr("hidden",false);
//       $('#table_month').attr("hidden",true);
//       $('#table_date').attr("hidden",false);
//       $('.togglehide').attr("hidden",false);
//       $('.red-btn').attr("hidden",false);
//       $('.red-btn2').attr("hidden",true);
//       $('#resource_search').attr("hidden",false);
//       $('#resource_search2').attr("hidden",true);
//   }
// });

// keep position after refresh
document.addEventListener("DOMContentLoaded", function(event) { 
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
});

window.onbeforeunload = function(e) {
    localStorage.setItem('scrollpos', window.scrollY);
};

//evaluation calendar refresh
function evaluationrefresh(){
      eval_date = $('#evaluation_calendar').val();
  $.ajax({
        url: "/bleach_admin/ajax/evaluation-calendar-date/",
        data: {
        'evaluation_calendar_date': eval_date
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
          console.log(data.evaluationdetails);
          
          $(".eval-table tbody").html(data.evaluationdetails);
        }
  })
};

//cleaning calendar refresh
function cleaningrefresh(){
  console.log("refr")
  cleaning_date = $('#cleaning_calendar').val();
  $.ajax({
        url: "/bleach_admin/ajax/cleaning-calendar-date/",
        data: {
        'cleaning_calendar_date': cleaning_date
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
          console.log(data.cleaningdetails);
          $("#cleaning_table tbody").html(data.cleaningdetails);
        }
  })
};

//required readonly support
$(".readonly").keydown(function(e){
        e.preventDefault();
    });