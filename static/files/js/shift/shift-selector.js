
//var url='https://my.bleachkw.com';
// //var url = 'https://my.bleachkw.com';
// //var url = 'https://my.bleachkw.com';
////var url='http://localhost:8000';
var shiftId = ''
 //var resourceList=[];
// var cleanerList=[];
// var teamLeaderList=[];
// var leaveSheet=[];
// var leaveId='';
// var modaluser='';
// var newResource=[];
// var dateCounter=0;
// getUsers();

// $(".lv-result-box-2").hide();
// $(".lv-conf-2").hide();
// $('.lv-modal-2').hide();
// var modalBox=false;
// var DateTime = luxon.DateTime;

// var selectedId = [];
// var days=['M','T','W','T','F','S','S'];
// var currentMonth = DateTime.local().month; //CURRENT MONTH
// var currentYear=DateTime.local().year;   //CURRENT YEAR
// var currentDay=DateTime.local(2017, 10, 30).weekday; //CURRENT DAY

// $('#lv-month-select-2').text(DateTime.local().monthLong+' '+ DateTime.local().year);
// var resources=[];
// var selectedDates=[];
// var resourceLeave=[];

/** Define Time slots */
const app=  new Vue({

    el: '#app',
   
    delimiters: ['<%', '%>'],  
    data: {
        
        cl_cleaning_hr:'',
        cl_start_time:'',
        time_slots:[
            {
                start_time:"12:00 AM",
                end_time:"02:00 AM"
            },
            {
                start_time:"02:00 AM",
                end_time:"04:00 AM"
            },
            {
                start_time:"04:00 AM",
                end_time:"06:00 AM"
            },
            {
                start_time:"06:00 AM",
                end_time:"08:00 AM"
            },  {
                start_time:"08:00 AM",
                end_time:"10:00 AM"
            },
            {
                start_time:"10:00 AM",
                end_time:"12:00 PM"
            },  {
                start_time:"12:00 PM",
                end_time:"02:00 PM"
            },
            {
                start_time:"02:00 PM",
                end_time:"04:00 PM"
            },
            {
                start_time:"04:00 PM",
                end_time:"06:00 PM"
            }
            ,
            {
                start_time:"06:00 PM",
                end_time:"08:00 PM"
            },
            {
                start_time:"08:00 PM",
                end_time:"10:00 PM"
            },
            {
                start_time:"10:00 PM",
                end_time:"12:00 AM"
            }
        ],
        selected_slot:[]
    },
    methods:{
        selectSlot(slot){
            this.selected_slot.push(slot)
        },
        removeSlot(slot){
            var index=this.selected_slot.indexOf(slot)
           
            this.selected_slot.splice(index,1)
        },
        checkSlot(slot){
            var nextslot=slot+1
            var prevslot=slot-1
            if(this.selected_slot.length<1){
                return true
            }
            else{
                
                if(this.selected_slot.includes(nextslot)||this.selected_slot.includes(prevslot)){
                    return true
                }
                else{
                    return false
                }
            }
        }
    }

})
/*Dropdown Menu*/
$('.ls-dropdown').click(function () {
    $(this).attr('tabindex', 1).focus();
    $(this).toggleClass('active');
    $(this).find('.ls-dropdown-menu').slideToggle(300);
});
$('.ls-dropdown').focusout(function () {
    $(this).removeClass('active');
    $(this).find('.ls-dropdown-menu').slideUp(300);
});
$('.ls-dropdown .ls-dropdown-menu li').click(function () {
    $(this).parents('.ls-dropdown').find('span').text($(this).text());
    $(this).parents('.ls-dropdown').find('input').attr('value', $(this).attr('id'));
});
/*End Dropdown Menu*/


 $('.ls-dropdown-menu li').click(function () {
     app.cl_start_time=$('#shift3_start_at').val()
 }); 


//Initialization of data
var shiftSheet=[]
var shiftList=[]
function getInitDatasShift(){
    $('.lv-loader').show()
 
    $('.day-head').remove();
    $('.lv-rows').remove();

for(var i=0;i<resourceList.length;i++){
    selectedDates.push({name:'',dates:[]})
}

var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;

var found=false;
//var noOfWeek=noOfDays/7;

for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;
    if(DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)=='F'){
        $('#lv-head-2-'+k).after('<th class="noBorder day-head" id="lv-head-2-'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-2-'+k).after('<th class="noBorder day-head" id="lv-head-2-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
}

for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    var noOfShift=0;
    $('#lv-body-head-2').append('<tr class="lv-rows" id="row-2'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text" id="no-shift-'+j+'">'+noOfShift+'</span></div> <img src="'+resourceList[j].photo_url+'"align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');

   
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        if(resourceList[j].shift.length>0)
        {
            for(var rs=0;rs<resourceList[j].shift.length;rs++){
               
                if(resourceList[j].shift[rs].date==today){
                    if(resourceList[j].shift[rs].date==today){
                        if(resourceList[j].shift[rs].shift1==true){
                         $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date"  onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-annual" id="lv-shift-date-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                        }
                        else if(resourceList[j].shift[rs].shift2==true){
                            $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date"  onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-weekly" id="lv-shift-date-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
 
                        }
                        else if(resourceList[j].shift[rs].shift3==true){
                            $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date"  onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-maternity" id="lv-shift-date-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
 
                        }
                        found=true;
                        noOfShift=noOfShift+1;
                     }
                }
              
               
            }
            
           

        }
        if(found==false)
        {
            $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date" onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date" id="lv-shift-date-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
            
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
    
    }
    $('#no-shift-'+j).text(noOfShift);
    $('.lv-loader').hide()
}
}


function checkTime(){
    var startTime = $('#shift3_start_at').val()
    var endTime = $('#shift3_end_at').val()
    var startval=parseInt(startTime.split(':')[0])
    var endval=parseInt(endTime.split(':')[0])
    console.log("start val"+startval+"endval:"+endval)
    if(!isNaN(startval) && !isNaN(endval)){
        if(startval<endval){
           
            $('#err-msg').hide()
            return true
        }
        else if(startval==0 && endval==0){
            $('#err-msg').hide()
            return true
        }
        else{
            $('#err-msg').show()
            return false
        }
    }
    else{
        $('#err-msg').hide()
        return false
    }
    
}

//Next Month and previous month caalculations
function nextMonthShift(){
    currentMonth=currentMonth+1;
    if(currentMonth>12){
        currentMonth=1;
        currentYear=currentYear+1;
       
    }
    $('#lv-month-select-2').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
    reCalcShift();

}
function previousMonthShift(){
    currentMonth=currentMonth-1;
    if(currentMonth<1){
        currentMonth=12;
        currentYear=currentYear-1;
       
    }
    $('#lv-month-select-2').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
   
    reCalcShift();    
}




//RECALCULATIONS
function reCalcShift(){
    $('.day-head').remove();
    $('.lv-rows').remove();
    var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;
//var noOfWeek=noOfDays/7;

for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;
    if(DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)=='F'){
        $('#lv-head-2-'+k).after('<th class="noBorder day-head" id="lv-head-2-'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-2-'+k).after('<th class="noBorder day-head" id="lv-head-2-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
  
}
for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    var noOfShift=0;
    $('#lv-body-head-2').append('<tr class="lv-rows" id="row-2'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text" id="no-shift-'+j+'">'+noOfShift+'</span></div> <img src="'+resourceList[j].photo_url+'" align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        // console.log(resourceList);
        if(resourceList[j].shift.length>0)
        {
            for(var rs=0;rs<resourceList[j].shift.length;rs++){
               
                if(resourceList[j].shift[rs].date==today){
                   if(resourceList[j].shift[rs].shift1==true){
                    $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date" onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-annual" id="lv-shift-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                   }
                   else if(resourceList[j].shift[rs].shift2==true){
                    $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date"  onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-weekly" id="lv-shift-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

                   }
                   else if(resourceList[j].shift[rs].shift3==true){
                    $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date"  onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date lv-maternity" id="lv-shift-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

                   }
                   found=true;
                   noOfShift=noOfShift+1;
                }
              
                
            }
            
           

        }
        if(found==false)
        {
            $('#row-2'+rsid).append('<td class="noBorder text-center lv-shift-date" onclick="selectDayShift(this)" id="lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-shift-date" id="lv-shift-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
           
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-2-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
       // console.log('i am running')
       // $('#row-1').append('<p>testing</p>')
    }
    $('#no-shift-'+j).text(noOfShift);

}
for(var sel=0;sel<selectedId.length;sel++){
    $('#'+selectedId[sel]).find('.lv-shift-date').addClass('lv-selected-date');
}

}




function reinitVal(){
    selectedDates=[];
    for(var i=0;i<resourceList.length;i++){
        selectedDates.push({name:'',dates:[]});
    }

}

//Select Day
function selectDayShift(el){
    var dayId=$(el).attr('id');
    dateCounter=dateCounter+1;
   console.log('day is is'+dayId)
    var userId=dayId.split('-')[3];
    console.log("user id is"+userId)
    var user=resourceList[userId].name;
    modalUser=resourceList[userId].id;
   console.log("resource details is"+resourceList[userId])
    selectedDates[userId].name=user;
    console.log("curent month :"+currentMonth.toString()+"current yr :"+currentYear.toString()+"shift date:"+$('#'+dayId).find('.lv-shift-date').text().toString())
    shiftId=getShiftId($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString(),userId);
    console.log(shiftId)
    console.log("hellooo")

    if($('#'+dayId).find('.lv-shift-date').hasClass('lv-weekend')){
        $('#'+dayId).find('.lv-shift-date').removeClass('lv-weekend');
    }
    if($('#'+dayId).find('.lv-shift-date').hasClass('lv-annual')){
      
        $('.modal-title').text('Shift 1');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-annual-text');
        $('.modal-date').text($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#ShiftModal').show();
        
    }
    if($('#'+dayId).find('.lv-shift-date').hasClass('lv-sick')){
        
        $('.modal-title').text('Sick Leave');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-sick-text');
        $('.modal-date').text($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#ShiftModal').show();
    }
    if($('#'+dayId).find('.lv-shift-date').hasClass('lv-maternity')){
        var shift_data={}
        for(var i=0;i<shiftSheet.length;i++){
            if(shiftSheet[i].id==shiftId){
                shift_data=shiftSheet[i]
                break;
            }
        }
        $('.modal-title').text('Custom Shift');
        $('#start_at').text('Start at : '+ tConvert(shift_data.shift3_start_at));
        $('#end_at').text('End at : '+ tConvert(shift_data.shift3_end_at));
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-maternity-text');
        $('.modal-date').text($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#ShiftModal').show();
    }
    if($('#'+dayId).find('.lv-shift-date').hasClass('lv-weekly')){
       
       
        $('.modal-title').text('Shift 2');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').addClass('lv-weekly-text');
        $('.modal-date').text($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#ShiftModal').show();
        dateCounter=dateCounter-1;
    }
    else{
    if(($('#'+dayId).find('.lv-shift-date').hasClass('lv-selected-date'))||($('#'+dayId).find('.lv-shift-date').hasClass('lv-maternity'))||($('#'+dayId).find('.lv-shift-date').hasClass('lv-sick'))||($('#'+dayId).find('.lv-shift-date').hasClass('lv-annual'))){
        $('#'+dayId).find('.lv-shift-date').removeClass('lv-selected-date');
        var index = selectedId.indexOf(dayId);
        var selectedIndex=selectedDates[userId].dates.indexOf($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        if (index !== -1) {
                selectedId.splice(index, 1);
              //  selectedData.dates.splice(selectedIndex,1);
                selectedDates[userId].dates.splice(selectedIndex,1);
                dateCounter=dateCounter-1;
        }
        dateCounter=dateCounter-1;
       if($('#'+dayId).find('.lv-shift-date').hasClass('is-weekend')){
            $('#'+dayId).find('.lv-shift-date').addClass('lv-weekend');
        
        }
        
     
    }
    else{
       
        $('#'+dayId).find('.lv-shift-date').addClass('lv-selected-date');
        selectedId.push(dayId);
       // selectedData.dates.push($('#'+dayId).find('.lv-shift-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString())
        selectedDates[userId].dates.push($('#'+dayId).find('.lv-shift-date').text()+'-'+currentMonth.toString()+'-'+currentYear.toString());
    }
}
    
    $('#ls-select-counter').text(dateCounter);
}


function clearAllShift(){
    
    dateCounter=0;
    $('#ls-select-counter').text(dateCounter);
    selectedId=[];
    resourceLeave=[];
    selectedDates=[];
    resourceList=[];
    reinitVal();
    getUsersShift();
}
function openForm(){
  
    $(".lv-result-box").show();
  
}
function closeForm(){
  
    $(".lv-result-box").hide();
  
}
function openConf(){
    $(".lv-conf").show();
    $("#lv-cancel-btn").hide();
}
function closeConf(){
    $(".lv-conf").hide();
    $("#lv-cancel-btn").show();
}



//get users 
function getUsersShift(){
    $('.lv-loader').show()
     // url ='https://my.bleachkw.com';
     url =api;
      resourceList=[];
      
    axios.get(url+'/api/leave-users-list/')
.then(function (response) {
  // handle success
  
  console.log(response);
  for(var i = 0; i < response.data.staffs.length; i++) {
    var staffData={};
    staffData['name'] = response.data.staffs[i].name;
    staffData['id']=response.data.staffs[i].id;
    staffData['user_type']=response.data.staffs[i].user_type;
    staffData['photo_url']=response.data.staffs[i].photo_url;
    staffData['shift']=[];
     
        resourceList.push(staffData); 
}
getShift();

})
.catch(function (error) {
  // handle error
  console.log(error);
})
}

// Add to shift 1
function addToShift1(){
           
        resourceLeave=[];
        shiftList=[]
        console.log("selected Dates are "+JSON.stringify(selectedDates))
        for(var i=0;i<selectedDates.length;i++){
            for (var j=0;j<selectedDates[i].dates.length;j++){
                var leaveSelected={};
                var leaveData={
                    type:$("#lv-result-content").text(),
                    date:selectedDates[i].dates[j]
                }
             //   leaveSelected['leave_type']=$("#lv-result-content").text().toUpperCase();
                var lvmonth=selectedDates[i].dates[j].split('-')[1];
                if(lvmonth.length<2){
                    lvmonth='0'+lvmonth;
                }
                var lvyear=selectedDates[i].dates[j].split('-')[2];
                var lvday=selectedDates[i].dates[j].split('-')[0];
                if(lvday.length<2){
                    lvday='0'+lvday;
                }
                leaveSelected['shift_date']=lvyear+'-'+lvmonth+'-'+lvday;
                leaveSelected['staff']=resourceList[i].id;
                leaveSelected['shift1']=true
                leaveSelected['shift2']=false
                leaveSelected['shift3']=false
                // leaveSelected['shift3_start_at']=null
                // leaveSelected['shift3_end_at']=null
                shiftList.push(leaveSelected);
               // resourceList[i].leave.push(leaveData);
            }
        }
    
        /* add leave */
    
        axios.post(url+'/api/shift-scheduler/',shiftList)
        .then(function (response) {
          // handle success
       
          resourceLeave=[];
          selectedDates=[];
          resourceList=[];
          shiftList=[];
          reinitVal();
          getUsersShift();
       
         
        
       // getInitDatas();
        })
        .catch(function (error) {
          // handle error
          console.log(error);
        })
        
       
        selectedDates=[];
     
        $(".lv-result-box").hide();
        dateCounter=0;
          $('#ls-select-counter').text(dateCounter);
      
    
}
function openCustomModal(){
    $('#customModal').show();
}
/** time converter */
function tConvert (time) {
    // Check correct time format and split into components
    time = time.toString ().match (/^([01]\d|2[0-3])(:)([0-5]\d)(:[0-5]\d)?$/) || [time];
  
    if (time.length > 1) { // If time format correct
      time = time.slice (1);  // Remove full string match value
      time[5] = +time[0] < 12 ? ' am' : ' pm'; // Set AM/PM
      time[0] = +time[0] % 12 || 12; // Adjust hours
    }
    return time.join (''); // return adjusted time or original string
  }
/** time converter ends here */
function addToShift3(){
    
    
   if(app.cl_cleaning_hr && app.cl_start_time){
    var start = Math.min( ...app.selected_slot )
    var end = Math.max( ...app.selected_slot )
    resourceLeave=[];
    shiftList=[]
    console.log("selected Dates are "+JSON.stringify(selectedDates))
    for(var i=0;i<selectedDates.length;i++){
        for (var j=0;j<selectedDates[i].dates.length;j++){
            var leaveSelected={};
            var leaveData={
                type:$("#lv-result-content").text(),
                date:selectedDates[i].dates[j]
            }
        
            var lvmonth=selectedDates[i].dates[j].split('-')[1];
            if(lvmonth.length<2){
                lvmonth='0'+lvmonth;
            }
            var lvyear=selectedDates[i].dates[j].split('-')[2];
            var lvday=selectedDates[i].dates[j].split('-')[0];
           
            if(lvday.length<2){
                lvday='0'+lvday;
            }
            var cleaning_hr=parseInt(app.cl_cleaning_hr)
            var start_date_time=moment(selectedDates[i].dates[j],'DD-MM-YYYY').format('DD-MM-YYYY')+' '+app.cl_start_time
            var end_date_time=moment(start_date_time,'DD-MM-YYYY hh:mm A').add(cleaning_hr,'hours').format('DD-MM-YYYY hh:mm A')
            //  if(app.time_slots[end].end_time=='12:00 AM'){
            //      var new_date=moment(selectedDates[i].dates[j],'DD-MM-YYYY').add(1,'days').format('DD-MM-YYYY')
            //      end_date_time=new_date+' '+app.time_slots[end].end_time
            //  }
            leaveSelected['shift_date']=lvyear+'-'+lvmonth+'-'+lvday;
            leaveSelected['staff']=resourceList[i].id;
            leaveSelected['shift1']=false
            leaveSelected['shift2']=false
            leaveSelected['shift3']=true
            leaveSelected['shift3_start_at']=start_date_time
            leaveSelected['shift3_end_at']=end_date_time
            shiftList.push(leaveSelected);
           
        }
    }
    /* add leave */

    axios.post(url+'/api/shift-scheduler/',shiftList)
    .then(function (response) {
      // handle success
      $('#customModal').hide()
      resourceLeave=[];
      selectedDates=[];
      resourceList=[];
      shiftList=[];
      app.selected_slot=[]
      app.cl_cleaning_hr=''
      app.cl_start_time=''
      $('#shift3_start_at').val(' ')
      
      reinitVal();
      getUsersShift();
      
     
    
   // getInitDatas();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
    
   
    selectedDates=[];
 
    $(".lv-result-box").hide();
    dateCounter=0;
      $('#ls-select-counter').text(dateCounter);
}
}
function addToShift2(){
           
    resourceLeave=[];
    shiftList=[]
    console.log("selected Dates are "+JSON.stringify(selectedDates))
    for(var i=0;i<selectedDates.length;i++){
        for (var j=0;j<selectedDates[i].dates.length;j++){
            var leaveSelected={};
            var leaveData={
                type:$("#lv-result-content").text(),
                date:selectedDates[i].dates[j]
            }
         //   leaveSelected['leave_type']=$("#lv-result-content").text().toUpperCase();
            var lvmonth=selectedDates[i].dates[j].split('-')[1];
            if(lvmonth.length<2){
                lvmonth='0'+lvmonth;
            }
            var lvyear=selectedDates[i].dates[j].split('-')[2];
            var lvday=selectedDates[i].dates[j].split('-')[0];
            if(lvday.length<2){
                lvday='0'+lvday;
            }
            leaveSelected['shift_date']=lvyear+'-'+lvmonth+'-'+lvday;
            leaveSelected['staff']=resourceList[i].id;
            leaveSelected['shift1']=false
            leaveSelected['shift2']=true
            leaveSelected['shift3']=false
            // leaveSelected['shift3_start_at']=null
            // leaveSelected['shift3_end_at']=null
            shiftList.push(leaveSelected);
           // resourceList[i].leave.push(leaveData);
        }
    }

    /* add leave */

    axios.post(url+'/api/shift-scheduler/',shiftList)
    .then(function (response) {
      // handle success
   
      resourceLeave=[];
      selectedDates=[];
      resourceList=[];
      shiftList=[];
      reinitVal();
      getUsersShift();
   
     
    
   // getInitDatas();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
    
   
    selectedDates=[];
 
    $(".lv-result-box").hide();
    dateCounter=0;
      $('#ls-select-counter').text(dateCounter);
  

}


//RESET ON TEAMINCHARGE,ALL,CLEANER
function resetResourcesShift(category){
    
    var newResource=[];
    if(category=='ALL')
        {  
            for(var i=0;i<resourceList.length;i++){
        
                newResource.push(resourceList[i]);
            }
        }
    
        else{
            if(category=='TEAM IN CHARGE')
        { 
            for(var i=0;i<resourceList.length;i++){
        
                if(resourceList[i].user_type=='TEAMINCHARGE'){
                    newResource.push(resourceList[i]);
                }
            }
            
        }
        else{
            if(category=='CLEANER')
            { 
                for(var i=0;i<resourceList.length;i++){
        
                    if(resourceList[i].user_type=='CLEANER'){
                        newResource.push(resourceList[i]);
                    }
                }
            }
        }
       
    }
    resourceList=newResource;
     
}





//get shifts
function getShift(){
    $('.lv-loader').show()
  //  url ='https://my.bleachkw.com';
  url =api;
    axios.get(url+'/api/shift-scheduler/')
.then(function (response) {
  // handle success
    for(var i=0;i<response.data.staffs.length;i++){
       
       var userIndex=userSearchShift(response.data.staffs[i].staff)
     
       // resourceList[userIndex].leave.push({date:'2-2-2021',type:'Annual Leave'});
      shiftSheet=response.data.staffs;
       var gt_year=response.data.staffs[i].shift_date.split('-')[0];
       var gt_month=response.data.staffs[i].shift_date.split('-')[1];
       var gt_day=response.data.staffs[i].shift_date.split('-')[2];
       if(gt_day[0]=='0'){
           gt_day=gt_day.substring(1);
       }
       if(gt_month[0]=='0'){
        gt_month=gt_month.substring(1);
    }
    if(userIndex!=undefined){

    
    resourceList[userIndex].shift.push({date:gt_day+'-'+gt_month+'-'+gt_year,shift1:response.data.staffs[i].shift1,shift2:response.data.staffs[i].shift2,shift3:response.data.staffs[i].shift3,shift3_start_at:response.data.staffs[i].shift3_start_at,shift3_end_at:response.data.staffs[i].shift3_start_at,shift_id:response.data.staffs[i].id});
    }    
}
   
    console.log(resourceList)
    $('.lv-loader').hide()
    getInitDatasShift();
   


})
.catch(function (error) {
  // handle error
  console.log(error);
})
}
function userSearchShift(key){
    for (var j=0; j < resourceList.length; j++) {
        if (resourceList[j].id == key) {
            return j;
        }
    }
}
function shiftSearch(staffId){
    for (var k=0; k < leaveSheet.length; k++) {
        if (leaveSheet[k].staff == staffId) {
          
            return leaveSheet[k].id;
        }
    }
}
function closeLeaveModal(){
    $('#leaveModal').hide();
    closeConf();

}
function closeShiftModal(){
    $('#ShiftModal').hide();
    closeConf();

}
function closeCustomModal(){
    $('#customModal').hide();
    closeConf();
}
 /*function closeCancelModal(){
     $('#cancelModal').hide();
     closeConf();

 }*/

function cancelShift(){
    console.log(shiftId)
      axios.get(url+'/api/shift-scheduler-delete/'+shiftId)
      .then(function (response) {
          console.log(response)
        // handle success
        resourceLeave=[];
        selectedDates=[];
        resourceList=[];
        reinitVal();
        getUsersShift();
       
       
        shiftId='';
      $('#ShiftModal').hide();
      dateCounter=0;
      $('#ls-select-counter').text(dateCounter);
      })
      .catch(function (error) {
        // handle error
        console.log(error);
      })
      closeConf();
  }

function getShiftId(ldate,staffid){
    console.log("resourceList is "+JSON.stringify(resourceList))
      for(var i=0;i<resourceList[staffid].shift.length;i++){
          if(resourceList[staffid].shift[i].date==ldate){
              return resourceList[staffid].shift[i].shift_id;
          }
      }
  }

