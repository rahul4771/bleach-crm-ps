$('#timepicker1').timepicker({icons: {
  time: "fa fa-clock",
  date: "fa fa-calendar",
  up: "fa fa-arrow-up",
  down: "fa fa-arrow-down",
  previous: "fa fa-chevron-left",
  next: "fa fa-chevron-right",
  today: "fa fa-clock",
  clear: "fa fa-trash-o"
}});
$(".chosen-select").chosen();
$("#bk-job-booking-btn").hide();
$("#bk-evaluation-btn").hide();
$(".bk-evaluation-form").hide();
$(".bk-job-booking-form").hide();
$(".bk-item-card").hide();
$(".bk-item-form").hide();
$(".bk-image-container").hide();
$("#bk-del-btn-1").hide();
$(".bk-stain-reason").hide();
$('.timepicker-12-hr').wickedpicker(); 


/* Date picker restriction */
var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();

    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var minDate = year + '-' + month + '-' + day;    
    $('#bk-date-job').attr('min', minDate);
    $('#bk-date').attr('min', minDate);

function selectCheck(){
    destroyAll();
    $(".bk-evaluation-form").hide();
    $(".bk-job-booking-form").hide();
    $(".bk-item-card").hide();
    $(".bk-item-form").hide();
    $(".bk-stain").hide();
    $(".bk-image-container").hide();
    deactivateJob();
    deactivateEval();
    $("#bk-evaluation-btn").show();
    var selectedVal=$( "#bk-service option:selected" ).text();
   
    if(selectedVal=='Sofa Cleaning'||selectedVal=='Mattress Cleaning'||selectedVal=='Kitchen Cleaning'||selectedVal=='Carpet Cleaning'||selectedVal=='Sterilization'){
        $('#bk-title-1').html(selectedVal.split(' ')[0]+' 1')
        $("#bk-job-booking-btn").show();
        
        if(selectedVal=='Mattress Cleaning'){
            $('#bk-size-1').parent().replaceWith('<div class="input-group mb-3"><select class="form-select  mb-3 size" aria-label=".form-select-lg example " id="bk-size-1" name="bk-size-1" onchange="durationcalculation(this);"><option selected disabled>Select Size</option><option value="single">Single</option><option value="queen">Queen </option><option value="king">King </option> </select></div>')
        }
        else {
            if(selectedVal=='Sofa Cleaning')
            {
                $('#bk-size-1').parent().replaceWith('<div class="input-group mb-3"><input type="number" class="form-control size" placeholder="Size" aria-label="Size" aria-describedby="basic-addon2" id="bk-size-1" name="bk-size-1" onkeyup="durationcalculation(this);" required><span class="input-group-text" id="basic-addon2">Seater</span><input type="text" value="seater" name="bk-unit-1" id="bk-unit-1" style="display:none;"/> </div>')

            }
            else{
                $('#bk-size-1').parent().replaceWith('<div class="input-group mb-3"><input type="number" class="form-control size" placeholder="Size" aria-label="Size" aria-describedby="basic-addon2" id="bk-size-1" name="bk-size-1" onkeyup="durationcalculation(this);" required><span class="input-group-text" id="basic-addon2">㎡</span><input type="text" value="square meter" name="bk-unit-1" id="bk-unit-1"  style="display:none;"/> </div>')

            }

        }
        if(selectedVal=='Kitchen Cleaning'){
          
            $('#bk-stain-1-1').parent().replaceWith('<div class="d-flex w-100" ><div class="px-2">Oil residue ?</div><input type="radio"  name="bk-oil_residue-1" id="bk-stain-1-1"   value="true"><label for="bk-stain-1-1">yes</label><br><input type="radio"  name="bk-oil_residue-1" id="bk-stain-1-2"  value="false" checked><label for="bk-stain-1-2">no</label><br> </div>');

        }
        else{
            $('#bk-stain-1-1').parent().replaceWith('<div class="d-flex w-100" ><div class="px-2">Any stain?</div><input type="radio"  name="bk-stain-1" id="bk-stain-1-1"  onchange="checkStain(this)" value="yes" ><label for="bk-stain-1-1">yes</label><br><input type="radio"  name="bk-stain-1" id="bk-stain-1-2"  value="no" onchange="checkStain(this)" checked><label for="bk-stain-1-2">no</label><br></div>');
        }
       
    }
    else{
        $("#bk-job-booking-btn").hide();
    }
}
function showEvaluation() {
    
    activateEval();
    deactivateJob();
    

};
function showJobBooking() {
    
    activateJob();
    deactivateEval();
    
    //update service type
    service_type = $('#bk-service').val();
    $('#service_type_id').val(service_type);
};
function activateEval(){
    $(".bk-evaluation-form").show();
    $("#bk-evaluation-btn").removeClass("btn-outline-primary");
    $("#bk-evaluation-btn").addClass("btn-primary");
    $(".bk-item-card").hide();
    $(".bk-item-form").hide();
    $(".bk-stain").hide();
    $(".bk-image-container").hide();
}
function deactivateEval(){
    $(".bk-evaluation-form").hide();
    $("#bk-evaluation-btn").addClass("btn-outline-primary");
    $("#bk-evaluation-btn").removeClass("btn-primary");
}
function activateJob(){
    $(".bk-job-booking-form").show();
    $("#bk-job-booking-btn").removeClass("btn-outline-primary");
    $("#bk-job-booking-btn").addClass("btn-primary");
    $(".bk-item-card").show();
    $(".bk-item-form").show();
    $(".bk-stain").show();
    $(".bk-image-container").show();
}
function deactivateJob(){
    $(".bk-job-booking-form").hide();
    $("#bk-job-booking-btn").addClass("btn-outline-primary");
    $("#bk-job-booking-btn").removeClass("btn-primary");
}

function checkStain(elem){
   
  
    let stain_id=$(elem).attr('id').split('-')[2];
    console.log("elem is "+$(elem).val());
    if($(elem).val()=='yes'){
       console.log("id is"+stain_id)
       $("input[name='bk-stain-"+stain_id+"']")[0].checked=true;
       $("input[name='bk-stain-"+stain_id+"']")[1].checked=false;
        $("[name='bk-stain-reason-"+stain_id+"'"+"]").parent('.bk-stain-reason').show();
        
    }
    else{
       /* $("#bk-stain-reason-"+stain_id).parent('.bk-stain-reason').hide();*/
       $("input[name='bk-stain-"+stain_id+"']")[1].checked=true;
       $("input[name='bk-stain-"+stain_id+"']")[0].checked=false;
       $("[name='bk-stain-reason-"+stain_id+"'"+"]").parent('.bk-stain-reason').hide();
    }
}
function destroyAll(){
    var formItems = [];
    $("#bk-main-form > div").each((index, elem) => {
             formItems.push(elem.id);
        });
        for(var i=1;i<formItems.length;i++){
            if(formItems[i].length>2 && formItems[i]!='bk-item-1'){
                $('#'+formItems[i]).remove();
            }
            
        }
       counter=1;
        
}
function selectAddress(addr){
    var addrId=$(addr).attr('id');
   var addrIndex=addrId.split('-')[2];
   console.log("addrr index is "+addrIndex);
   if($('#bk-check-box-'+addrIndex).hasClass('bk-check-box-active')){
    
            $('#bk-check-box-'+addrIndex).removeClass('bk-check-box-active');
       $('#location').val('');
       $('#gps').val('');
       $('#location').val('');
       $('#governorate').val('');
       $('#area').val('');
       $('#address').val('');
       $('#floor').val('');
       $('#building').val('');
       $('#block').val('');
       $('#street').val('');
       $('#address_id').val('');
       $('#id_governorate').val('');
       $('#id_area').empty();
       $("#id_area").append($('<option>', {
                      value: "", 
                      text: "Choose Area"
                    }));
       $('#id_area').val('');
}
else{
    if($('.bk-check-box').hasClass('bk-check-box-active')){
       
        $('.bk-check-box').removeClass('bk-check-box-active');
        $('#bk-check-box-'+addrIndex).addClass('bk-check-box-active');
       }
       
       else{
             $('#bk-check-box-'+addrIndex).addClass('bk-check-box-active');
       }
       $('#location').val($('#bk-location-'+addrIndex).text());
       $('#gps').val($('#bk-gps-'+addrIndex).text());
       $('#location').val($('#bk-location-'+addrIndex).text());
       $('#governorate').val($('#bk-governorateId-'+addrIndex).text());
       $('#area').val($('#bk-areaId-'+addrIndex).text());
       $('#address').val($('#bk-address-'+addrIndex).text());
       $('#floor').val($('#bk-floor-'+addrIndex).text());
       $('#building').val($('#bk-building-'+addrIndex).text());
       $('#block').val($('#bk-block-'+addrIndex).text());
       $('#street').val($('#bk-street-'+addrIndex).text());
       
       governorate_id = $('#bk-governorateID-'+addrIndex).text();
       area_id        = $('#bk-areaID-'+addrIndex).text();
       $.ajax({

        url: "/agent/ajax/getarea/",

        data: {'governorate_id':governorate_id}, 

        dataType: 'json',

        success: function (data) { 

          ajax_ret_areas = data;     
          $("#id_area").empty();

        $("#id_area").append($('<option>', {
                      value: "", 
                      text: "Choose Area"
                    })); 

        $.each( ajax_ret_areas, function( key, values ) {

            if(area_id == key)
            {
              $("#id_area").append($('<option>', {        
                      value: key,   
                      text: values,
                      selected: true  
                    }));   
            }
            else
            {
              $("#id_area").append($('<option>', {        
                      value: key,   
                      text: values   
                    })); 
            }

        });
        }  
              });

       $('#address_id').val($('#bk-addressID-'+addrIndex).text());
       $('#id_governorate').val($('#bk-governorateID-'+addrIndex).text());
}
   
   
  
   

}  

  
 
//Cleaning booking scripts
function durationcalculation(params)
  {
    //to find total size
    sectioncounter = $('#sectioncounter_id').val();
    total_estimated_size = 0
    for(i=1;i<=sectioncounter;i++)
    {
        size = $('#bk-size-'+i).val() 
        if (size == '')
        {
            size = 0;
        }
        else if(size == 'single')
        {
          size = 1;
        }
        else if(size == 'king')
        {
          size = 2;
        }
        else if(size == 'queen')
        {
          size = 3;
        }

        total_estimated_size += parseFloat(size);
    }

    //Ajax for finding productivity of perticular service
    selected_service = $("#bk-service option:selected" ).text();
    $.ajax({

        url: "/customer/ajax/getserviceproductivity",

        data: {'service_type':selected_service,'total_estimated_size':total_estimated_size}, 

        dataType: 'json',

        success: function (data) {
            //find duration and no of cleaners based on productivity
            total_estimated_size = total_estimated_size
            productivity         = data['perhour_cleaning'];
            
            //optimal manhour finding
            manhour = parseInt(total_estimated_size/productivity)
            r       = 2 ** (manhour.toString().length-1)
            mod     = manhour%r
            
            if (mod > parseInt(r/2))
            {
              n= manhour+(r-mod);
            }
            else
            {
              n = manhour-mod;
            }
            console.log(n,"n");
            for(i=1;i<parseInt(n ** (1/2))+1;i++)
            {
              if(n%i == 0)
                {
                  pair = [i,n/i];
                }
            }
            console.log(pair,"pair");
            max_cleaners = data['max_cleaners']
            
            duration_list = [];
            upper_loop    = 2;
            lower_loop    = 2;
            middle_element=pair[0]

            if(middle_element<=max_cleaners)
            {
              duration_list.push(pair);
              //upperloop and lowerloop setup
              for(i=1;i<=2;i++)
              {
                if((middle_element-i)<=0)
                {
                  upper_loop = upper_loop+(2-i)+1;
                  lower_loop = lower_loop-((2-i)+1)
                } 
                if((middle_element+i) > max_cleaners)
                {
                  lower_loop = lower_loop+(2-i)+1;
                  upper_loop = upper_loop-((2-i)+1)
                }
              }
              console.log(upper_loop,"upperloop")
              console.log(lower_loop,"lowerloop")
              //lower
              for(i=1;i<=lower_loop;i++)
              {
                if((middle_element-i)>0 && (middle_element-i) <= max_cleaners)
                {
                  duration_list.push([(middle_element-i),n/(middle_element-i)])
                }
              }
              //upper
              for(i=1;i<=upper_loop;i++)
              {
                if((middle_element+i)>0 && (middle_element+i) <= max_cleaners)
                {
                  duration_list.push([(middle_element+i),n/(middle_element+i)])
                } 
              }
            }

            
            else
            {
              middle_element = max_cleaners;
              duration_list.push([(middle_element),n/(middle_element)])
              for(i=1;i<=5;i++)
              {
                if((middle_element-i)>0)
                {
                  duration_list.push([(middle_element-i),n/(middle_element-i)])
                }
              }
            }
            console.log(duration_list)

            //APPEND SLOTE
            $("#bk-duration").empty()
            $("#bk-duration").append($('<option>', {        
                      value: "",   
                      text: "Duration"  
                    }));
            for(i=0;i<duration_list.length;i++)
              {
                if(duration_list[i][1]>10)
                {
                  total_days      = parseInt(duration_list[i][1]/10)+1;
                  total_duration  = duration_list[i][1]/total_days;
                  total_cleaners  = duration_list[i][0];
                }
                else
                {
                  total_days      = 1
                  total_duration  = duration_list[i][1];
                  total_cleaners  = duration_list[i][0];
                }
                //round off total duration
                var inv        = 1.0 / .5;
                total_duration = Math.round(total_duration * inv) / inv;
                
                //show to users
                total_minutes     = (total_duration.toFixed(2)*60).toFixed(0)
                converted_hours   = Math.floor(total_minutes / 60);          
                converted_minutes = total_minutes % 60;

                if(converted_hours >= 1)
                    {
                        $("#bk-duration").append($('<option>', {        
                            value: total_cleaners+"_cleaners-"+total_duration.toFixed(2)+"_Hours-"+total_days+"_Days",   
                            text: converted_hours+" Hours "+converted_minutes+" Minutes "+total_days+" Days "  
                          }));
                    }
                }
            //total price
            totalprice = data['total_price'];
            $('#bk-total-price').html(totalprice);
            $('#bk-total-cost').val(totalprice);

                   }
         });

  } 
  
  
//to mark busy dates
$('#bk-duration,#timepicker1').change(function()
{
  booking_time      = $("#timepicker1").val();
  duration_cleaners = $('#bk-duration').val().split('-');
  cleaning_duration = duration_cleaners[0].replace("_cleaners","");
  number_of_cleaner = duration_cleaners[1].replace("_Hours","");
  number_of_days    = duration_cleaners[2].replace("_Days","");

  service_type      = $("#bk-service option:selected" ).text();
  
  $.ajax({
            url: "/agent/ajax/scheduled/dates/",
            data: {
                'booking_time':booking_time,
                'cleaning_duration':cleaning_duration,
                'number_of_cleaner':number_of_cleaner,  
                'service_type':service_type,
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_dates) {
                console.log(data_dates,"dates1")
                disableSpecificDates = Object.keys(data_dates['cleaners_busy_dates']).concat(Object.keys(data_dates['leaders_busy_dates']))

                //disable date
                $(function () {
                $("#bk-date-job").datepicker({ 
                    multidate: number_of_days,
                    closeOnDateSelect: true,
                    format: "dd-mm-yyyy",
                    minDate:new Date(),
                    startDate:new Date(), 

                    beforeShowDay: function(date){
                    dmy = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear();
                    if(disableSpecificDates.indexOf(dmy) != -1){
                    return false;
                    }
                    else{
                    return true;
                    }
                    },

                });
                });
            }
            
        });
})

