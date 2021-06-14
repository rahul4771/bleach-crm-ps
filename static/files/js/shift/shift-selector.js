
// var url='https://test.bleach-kw.com';
// //var url = 'https://my.bleachkw.com';
// //var url = 'http://127.0.0.1:8000';
// //var url='http://localhost:8000';

// var resourceList=[];
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




//Initialization of data
function getInitDatasShift(){
   
 
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
        $('#lv-head-2'+k).after('<th class="noBorder day-head" id="lv-head-2'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-2'+k).after('<th class="noBorder day-head" id="lv-head-2'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
}

for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    
    $('#lv-body-head-2').append('<tr class="lv-rows" id="row-2'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"></div> <img src="'+resourceList[j].photo_url+'"align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');

   
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        if(resourceList[j].shift.length>0)
        {
            for(var rs=0;rs<resourceList[j].shift.length;rs++){
               
                if(resourceList[j].shift[rs].date==today){
                    if(resourceList[j].shift[rs].date==today){
                        if(resourceList[j].shift[rs].shift1==true){
                         $('#row-2'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                        }
                        else if(resourceList[j].shift[rs].shift2==true){
                            $('#row-2'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
 
                        }
                        found=true;
                     }
                }
              
                
            }
            
           

        }
        if(found==false)
        {
            $('#row-2'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
            
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
    
    }

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
    reCalc();

}
function previousMonthShift(){
    currentMonth=currentMonth-1;
    if(currentMonth<1){
        currentMonth=12;
        currentYear=currentYear-1;
       
    }
    $('#lv-month-select-2').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
   
    reCalc();    
}




//RECALCULATIONS
function reCalc(){
    $('.day-head').remove();
    $('.lv-rows').remove();
    var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;
//var noOfWeek=noOfDays/7;

for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;
    if(DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)=='F'){
        $('#lv-head-2'+k).after('<th class="noBorder day-head" id="lv-head-2'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-2'+k).after('<th class="noBorder day-head" id="lv-head-2'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
  
}
for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    $('#lv-body-head-2').append('<tr class="lv-rows" id="row-2'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"></div> <img src="'+resourceList[j].photo_url+'" align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        // console.log(resourceList);
        if(resourceList[j].shift.length>0)
        {
            for(var rs=0;rs<resourceList[j].shift.length;rs++){
               
                if(resourceList[j].shift[rs].date==today){
                   if(resourceList[j].shift[rs].shift1==true){
                    $('#row-2'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                   }
                   else if(resourceList[j].shift[rs].shift2==true){
                    $('#row-2'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

                   }
                   found=true;
                }
              
                
            }
            
           

        }
        if(found==false)
        {
            $('#row-2'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDayShift(this)" id="lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
           
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-2'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
       // console.log('i am running')
       // $('#row-1').append('<p>testing</p>')
    }

}
for(var sel=0;sel<selectedId.length;sel++){
    $('#'+selectedId[sel]).find('.lv-date').addClass('lv-selected-date');
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
   
    var userId=dayId.split('-')[2];
    var user=resourceList[userId].name;
    modalUser=resourceList[userId].id;
  
    selectedDates[userId].name=user;
    shiftId=getShiftId($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString(),userId);
    console.log(shiftId)

    if($('#'+dayId).find('.lv-date').hasClass('lv-weekend')){
        $('#'+dayId).find('.lv-date').removeClass('lv-weekend');
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-annual')){
      
        $('.modal-title').text('Annual Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-annual-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('.lv-modal').show();
        
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-sick')){
        
        $('.modal-title').text('Sick Leave');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-sick-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('.lv-modal').show();
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-maternity')){
        
        $('.modal-title').text('Maternity/Paternity Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-maternity-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('.lv-modal').show();
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-weekly')){
       
       
        $('.modal-title').text('Weekly Off');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').addClass('lv-weekly-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('.lv-modal').show();
        dateCounter=dateCounter-1;
    }
    else{
    if(($('#'+dayId).find('.lv-date').hasClass('lv-selected-date'))||($('#'+dayId).find('.lv-date').hasClass('lv-maternity'))||($('#'+dayId).find('.lv-date').hasClass('lv-sick'))||($('#'+dayId).find('.lv-date').hasClass('lv-annual'))){
        $('#'+dayId).find('.lv-date').removeClass('lv-selected-date');
        var index = selectedId.indexOf(dayId);
        var selectedIndex=selectedDates[userId].dates.indexOf($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        if (index !== -1) {
                selectedId.splice(index, 1);
              //  selectedData.dates.splice(selectedIndex,1);
                selectedDates[userId].dates.splice(selectedIndex,1);
                dateCounter=dateCounter-1;
        }
        dateCounter=dateCounter-1;
       if($('#'+dayId).find('.lv-date').hasClass('is-weekend')){
            $('#'+dayId).find('.lv-date').addClass('lv-weekend');
        
        }
        
     
    }
    else{
       
        $('#'+dayId).find('.lv-date').addClass('lv-selected-date');
        selectedId.push(dayId);
       // selectedData.dates.push($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString())
        selectedDates[userId].dates.push($('#'+dayId).find('.lv-date').text()+'-'+currentMonth.toString()+'-'+currentYear.toString());
    }
}
    
    $('#select-counter').text(dateCounter);
}


function clearAll(){
    
    dateCounter=0;
    $('#select-counter').text(dateCounter);
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
function applyLeave(){
    resourceLeave=[];
    for(var i=0;i<selectedDates.length;i++){
        for (var j=0;j<selectedDates[i].dates.length;j++){
            var leaveSelected={};
            var leaveData={
                type:$("#lv-result-content").text(),
                date:selectedDates[i].dates[j]
            }
            leaveSelected['leave_type']=$("#lv-result-content").text().toUpperCase();
            var lvmonth=selectedDates[i].dates[j].split('-')[1];
            if(lvmonth.length<2){
                lvmonth='0'+lvmonth;
            }
            var lvyear=selectedDates[i].dates[j].split('-')[2];
            var lvday=selectedDates[i].dates[j].split('-')[0];
            if(lvday.length<2){
                lvday='0'+lvday;
            }
            leaveSelected['leave_date']=lvyear+'-'+lvmonth+'-'+lvday;
            leaveSelected['staff']=resourceList[i].id;
            resourceLeave.push(leaveSelected);
            resourceList[i].leave.push(leaveData);
        }
    }

    /* add leave */

    axios.post(url+'/api/leave-scheduler/',resourceLeave)
    .then(function (response) {
      // handle success
   
      resourceLeave=[];
      selectedDates=[];
      resourceList=[];
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
      $('#select-counter').text(dateCounter);
  
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
    
      url ='http://127.0.0.1:8000';
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
    
    url ='http://127.0.0.1:8000';
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
    resourceList[userIndex].shift.push({date:gt_day+'-'+gt_month+'-'+gt_year,shift1:response.data.staffs[i].shift1,shift2:response.data.staffs[i].shift2,shift_id:response.data.staffs[i].id});
    }
   
    console.log(resourceList)
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
// function closeCancelModal(){
//     $('#cancelModal').hide();
//     closeConf();

// }

// function cancelLeave(){
    
//       axios.get(url+'/api/leave-scheduler-delete/'+leaveId)
//       .then(function (response) {
//         // handle success
//         resourceLeave=[];
//         selectedDates=[];
//         resourceList=[];
//         reinitVal();
//         getUsersShift();
       
       
//       leaveId='';
//       $('.lv-modal').hide();
//       dateCounter=0;
//       $('#select-counter').text(dateCounter);
//       })
//       .catch(function (error) {
//         // handle error
//         console.log(error);
//       })
//       closeConf();
//   }

function getShiftId(ldate,staffid){
      for(var i=0;i<resourceList[staffid].shift.length;i++){
          if(resourceList[staffid].shift[i].date==ldate){
              return resourceList[staffid].shift[i].shift_id;
          }
      }
  }

