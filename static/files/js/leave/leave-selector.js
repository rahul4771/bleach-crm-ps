
//var url='https://my.bleachkw.com';
//var url = 'https://test.bleach-kw.com';
//var url = 'http://127.0.0.1:8000';
var url=api;

var resourceList=[];
var cleanerList=[];
var teamLeaderList=[];
var leaveSheet=[];
var leaveId='';
var modaluser='';
var newResource=[];
var dateCounter=0;
getUsers();

$(".lv-result-box").hide();
$(".lv-conf").hide();
$('#leaveModal').hide();
var modalBox=false;
var DateTime = luxon.DateTime;

var selectedId = [];
var days=['M','T','W','T','F','S','S'];
var currentMonth = DateTime.local().month; //CURRENT MONTH
var currentYear=DateTime.local().year;   //CURRENT YEAR
var currentDay=DateTime.local(2017, 10, 30).weekday; //CURRENT DAY

$('#lv-month-select').text(DateTime.local().monthLong+' '+ DateTime.local().year);
var resources=[];
var selectedDates=[];
var resourceLeave=[];


function getInitDatas(){
   
 
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
        $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
}

for (var j=0;j<resourceList.length;j++){
    var noOfLeave=0;
    var rsid=j+1;
    
    $('#lv-body-head').append('<tr class="lv-rows" id="row-'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text" id="no-leave-'+j+'">'+noOfLeave+'</span></div> <img src="'+resourceList[j].photo_url+'"align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');

   
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();

        
        if(resourceList[j].leave.length>0)
        {
            for(var rs=0;rs<resourceList[j].leave.length;rs++){
               
               
                    if(resourceList[j].leave[rs].date==today){
                       
                        if(resourceList[j].leave[rs].type=='ANNUAL LEAVE'){
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                           }
                           else if(resourceList[j].leave[rs].type=='WEEKLY OFF'){
                              
                                   $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
               
                                  }
                                  else if(resourceList[j].leave[rs].type=='NOT PAID'||resourceList[j].leave[rs].type=='MATERNITY/PATERNITY'){
                                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-maternity" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                                   }
                                      else  if(resourceList[j].leave[rs].type=='SICK LEAVE'){
                                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-sick" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                    
                                       }
                                       else  if(resourceList[j].leave[rs].type=='COVID LEAVE'){
                                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-covid" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                    
                                       }
                                       else  if(resourceList[j].leave[rs].type=='ABSENT'){
                                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-absent" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                    
                                       }
                                      
                                          
                                      
                             
                       
                       
                       
     
                        found=true;
                        noOfLeave=noOfLeave+1;
                     }
                
              
                
            }
            
           

        }
        /* To set occupied dates*/
        if(resourceList[j].occupied.length>0)
        {
            for(var rs=0;rs<resourceList[j].occupied.length;rs++){
               
                if(resourceList[j].occupied[rs].start_at==today || resourceList[j].occupied[rs].end_at==today){
                   
                    
                        if ($('#lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear)[0]){
                          
                        } else {
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="openOccupied(this)" data-staff="'+j+'" data-date="'+today+'"  id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-occupied" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');    
                        }
                        
                                 
                     
                     found=true;  
                     
                }
              
                
            }
    
        } 
        if(found==false)
        {
           
            $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
            
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
    
    }
    $('#no-leave-'+j).text(noOfLeave);

}
}

function nextMonth(){
    currentMonth=currentMonth+1;
    if(currentMonth>12){
        currentMonth=1;
        currentYear=currentYear+1;
       
    }
    $('#lv-month-select').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
    resetLeaves()
    getLeave(currentMonth+'-'+currentYear)
   
}
function previousMonth(){
    currentMonth=currentMonth-1;
    if(currentMonth<1){
        currentMonth=12;
        currentYear=currentYear-1;
       
    }
    $('#lv-month-select').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
    resetLeaves()
    getLeave(currentMonth+'-'+currentYear)
  
    
}
function reCalc(){
    $('.day-head').remove();
    $('.lv-rows').remove();
    var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;
//var noOfWeek=noOfDays/7;

for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;
    if(DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)=='F'){
        $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day lv-friday">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

    }
   else{
    $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');

   }
  
}

for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    var noOfLeave=0;
    $('#lv-body-head').append('<tr class="lv-rows" id="row-'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text" id="no-leave-'+j+'">'+noOfLeave+'</span></div> <img src="'+resourceList[j].photo_url+'" align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">'+resourceList[j].user_type+'</div></div></td></tr>');
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        if(resourceList[j].leave.length>0)
        {
            for(var rs=0;rs<resourceList[j].leave.length;rs++){
               
                if(resourceList[j].leave[rs].date==today){
                
                if(resourceList[j].leave[rs].type=='ANNUAL LEAVE'){
                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                   }
                   else if(resourceList[j].leave[rs].type=='WEEKLY OFF'){
                  
                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

                   }
                   else if(resourceList[j].leave[rs].type=='NOT PAID'||resourceList[j].leave[rs].type=='MATERNITY/PATERNITY'){
                    
                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-maternity" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                       }
                       else if(resourceList[j].leave[rs].type=='SICK LEAVE'){
                      
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-sick" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
        
                           }
                           else if(resourceList[j].leave[rs].type=='COVID LEAVE'){
                      
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-covid" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
        
                           }
                           else if(resourceList[j].leave[rs].type=='ABSENT'){
                      
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-absent" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
        
                           }
                   
                   

                   found=true;
                   noOfLeave=noOfLeave+1;
                }
              
                
            }
            
           

        }
         /* To set occupied dates*/
         if(resourceList[j].occupied.length>0)
         {
             for(var rs=0;rs<resourceList[j].occupied.length;rs++){
                
                 if(resourceList[j].occupied[rs].start_at==today || resourceList[j].occupied[rs].end_at==today){
                    
                        
                         if ($('#lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear)[0]){
                         
                         } else {
                             $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="openOccupied(this)" data-staff="'+j+'" data-date="'+today+'" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-occupied" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');    
                         }
                         
                                  
                      
                      found=true;  
                      
                 }
               
                 
             }
     
         } 
        if(found==false)
        {
            $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
           
        }
        if(DateTime.local(currentYear, currentMonth, i).weekdayShort.substring(0,1)=='F'){
            $('#lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('lv-weekend');
            $('#lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear).addClass('is-weekend');

        }
      
      
    }
    $('#no-leave-'+j).text(noOfLeave);

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
function selectDay(el){
    var dayId=$(el).attr('id');
    dateCounter=dateCounter+1;
   
    var userId=dayId.split('-')[2];
    var user=resourceList[userId].name;
    modalUser=resourceList[userId].id;
  
    selectedDates[userId].name=user;
    leaveId=getLeaveId($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString(),userId);
  
    if($('#'+dayId).find('.lv-date').hasClass('lv-weekend')){
        $('#'+dayId).find('.lv-date').removeClass('lv-weekend');
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-annual')){
     
        $('.modal-title').text('Annual Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').removeClass('lv-covid-text');
        $('.modal-title').removeClass('lv-absent-text');
        $('.modal-title').addClass('lv-annual-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#leaveModal').show();
        dateCounter=dateCounter-1;
    }
   else if($('#'+dayId).find('.lv-date').hasClass('lv-sick')){
     
        $('.modal-title').text('Sick Leave');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').removeClass('lv-covid-text');
        $('.modal-title').removeClass('lv-absent-text');
        $('.modal-title').addClass('lv-sick-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#leaveModal').show();
        dateCounter=dateCounter-1;
    }
    else if($('#'+dayId).find('.lv-date').hasClass('lv-maternity')){
       
        $('.modal-title').text('Not Paid Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').removeClass('lv-covid-text');
        $('.modal-title').removeClass('lv-absent-text');
        $('.modal-title').addClass('lv-maternity-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
       
        $('#leaveModal').show();
        dateCounter=dateCounter-1;
    }
    else if($('#'+dayId).find('.lv-date').hasClass('lv-weekly')){
       
       
        $('.modal-title').text('Weekly Off');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-covid-text');
        $('.modal-title').removeClass('lv-absent-text');
        $('.modal-title').addClass('lv-weekly-text');
        
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#leaveModal').show();
      
        dateCounter=dateCounter-1;
    }
   
    else if($('#'+dayId).find('.lv-date').hasClass('lv-absent')){
       
       
        $('.modal-title').text('Absent');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-covid-text');
        $('.modal-title').addClass('lv-absent-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#leaveModal').show();
       
        dateCounter=dateCounter-1;
    }
    else if($('#'+dayId).find('.lv-date').hasClass('lv-covid')){
       
       
        $('.modal-title').text('Covid Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-absent-text');
        $('.modal-title').addClass('lv-covid-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
        $('#leaveModal').show();
       
        dateCounter=dateCounter-1;
    }
    else{
    if(($('#'+dayId).find('.lv-date').hasClass('lv-selected-date'))||($('#'+dayId).find('.lv-date').hasClass('lv-maternity'))||($('#'+dayId).find('.lv-date').hasClass('lv-sick'))||($('#'+dayId).find('.lv-date').hasClass('lv-annual'))||($('#'+dayId).find('.lv-date').hasClass('lv-covid'))||($('#'+dayId).find('.lv-date').hasClass('lv-absent'))){
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
function openOccupied(occ_data){
    $('.occupied-modal-body').html('')
    var date=$(occ_data).data('date')
    var staff=$(occ_data).data('staff')
    date=moment(date,'D-MM-YYYY').format('YYYY-MM-DD')
  

    $('#occupied_staff_name').text(resourceList[staff].name)
    $('#occupied_date').text(moment(date,'YYYY-MM-DD').format('DD-MM-YYYY'))
    axios.get(url+'/api/leave-scheduler/popup/?staff_id='+resourceList[staff].id+'&occupied_date='+date)
    .then(function (response) {

        for(var i=0;i<response.data.detials.length;i++){
            $('.occupied-modal-body').append(`
            <div class="occupied-blc mt-10">
            <span class="occupied-blc-text primary-text" >`+response.data.detials[i].blc+`</span>
            <span class="occupied-blc-time ml-20"><i class="far fa-clock mr-10 primary-text"></i>`+response.data.detials[i].start_at.split(' ')[1]+' '+ response.data.detials[i].start_at.split(' ')[2]+`<i class="fas fa-hourglass-start ml-20 mr-10 primary-text"></i>`+response.data.detials[i].cleaning_hours+`hrs </span>
             <i class="far fa-edit ml-20 occupied-edit" onclick="resetCleaning(`+response.data.detials[i].id+`,'`+response.data.detials[i].start_at.split(' ')[0]+`',`+resourceList[staff].id+`)"></i>
           </div>
            `)
        }
        $('#occupiedModal').show()
   
      
     
    
   // getInitDatas();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
   
}
function openOccupiedByUrl(occ_date,staff){
    $('.occupied-modal-body').html('')
    var date=moment(occ_date,'DD-MM-YYYY').format('YYYY-MM-DD')
    var staff_index=userSearch(staff)
    if(staff_index){
    $('#occupied_staff_name').text(resourceList[staff_index].name)
    }
    $('#occupied_date').text(occ_date)
    axios.get(url+'/api/leave-scheduler/popup/?staff_id='+staff+'&occupied_date='+date)
    .then(function (response) {

        for(var i=0;i<response.data.detials.length;i++){
            $('.occupied-modal-body').append(`
            <div class="occupied-blc mt-10">
            <span class="occupied-blc-text primary-text" >`+response.data.detials[i].blc+`</span>
            <span class="occupied-blc-time ml-20"><i class="far fa-clock mr-10 primary-text"></i>`+response.data.detials[i].start_at.split(' ')[1]+' '+ response.data.detials[i].start_at.split(' ')[2]+`<i class="fas fa-hourglass-start ml-20 mr-10 primary-text"></i>`+response.data.detials[i].cleaning_hours+`hrs </span>
             <i class="far fa-edit ml-20 occupied-edit" onclick="resetCleaning(`+response.data.detials[i].id+`,'`+response.data.detials[i].start_at.split(' ')[0]+`',`+staff+`)"></i>
           </div>
            `)
        }
        $('#occupiedModal').show()
   
      
     
    
   // getInitDatas();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
   
}
function resetCleaning(id,occ_date,staff){
 window.location.href="/common/editcleaning/team/"+id+"/?cleaning_calendar_date="+occ_date+"&from=leave_scheduler&staff="+staff
}
function clearAll(){
    
    dateCounter=0;
    $('#select-counter').text(dateCounter);
    selectedId=[];
    resourceLeave=[];
    selectedDates=[];
    resourceList=[];
    reinitVal();
    getUsers();
}
function openForm(){
  
    $(".lv-result-box").show();
  
}
function closeOccupiedModal(){
    $('#occupiedModal').hide();
   

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
      getUsers();
   
     
    
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

function getUsers(){
    
    $('.lv-loader').show()
      resourceList=[];
  
    axios.get(url+'/api/leave-users-list/')
.then(function (response) {
  // handle success
  for(var i = 0; i < response.data.staffs.length; i++) {
    var staffData={};
    staffData['name'] = response.data.staffs[i].name;
    staffData['id']=response.data.staffs[i].id;
    staffData['user_type']=response.data.staffs[i].user_type;
    staffData['photo_url']=response.data.staffs[i].photo_url;
    staffData['leave']=[];
    staffData['occupied']=[]
  
    
     
        resourceList.push(staffData);
   
    
   
    

    
}



getLeave(moment().format('M-YYYY'));
const urlSearchParams = new URLSearchParams(window.location.search);
const params = Object.fromEntries(urlSearchParams.entries());
if(Object.keys(params).length>0){
    openOccupiedByUrl(params.cleaning_calendar_date,params.staff)
}

})
.catch(function (error) {
  // handle error
  console.log(error);
})
}
function resetResources(category){
   
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
function resetLeaves(){
    for(var i=0;i<resourceList.length;i++){
        resourceList[i].leave=[]
    }
}
function getLeave(current_date){
    $('.lv-loader').show()
    var month=current_date.split('-')[0]
    var year=current_date.split('-')[1]
    axios.get(url+'/api/leave-scheduler/?month='+month+'&year='+year)
.then(function (response) {
  // handle success
  
    for(var i=0;i<response.data.staffs.length;i++){
       
       var userIndex=userSearch(response.data.staffs[i].staff)
     
       // resourceList[userIndex].leave.push({date:'2-2-2021',type:'Annual Leave'});
      leaveSheet=response.data.staffs;
       var gt_year=response.data.staffs[i].leave_date.split('-')[0];
       var gt_month=response.data.staffs[i].leave_date.split('-')[1];
       var gt_day=response.data.staffs[i].leave_date.split('-')[2];
       if(gt_day[0]=='0'){
           gt_day=gt_day.substring(1);
       }
       if(gt_month[0]=='0'){
        gt_month=gt_month.substring(1);
    }
 
    
    
   if(userIndex != undefined ){
    resourceList[userIndex].leave.push({date:gt_day+'-'+gt_month+'-'+gt_year,type:response.data.staffs[i].leave_type,leave_id:response.data.staffs[i].id});
   }
   
    
    }
    for(var i=0;i<response.data.occupied.length;i++){
       
        var userIndex=userSearch(response.data.occupied[i].member)
      
        // resourceList[userIndex].leave.push({date:'2-2-2021',type:'Annual Leave'});
      
        var gt_start_year=response.data.occupied[i].start_at.split('-')[0];
        var gt_start_month=response.data.occupied[i].start_at.split('-')[1];
        var gt_start_day=response.data.occupied[i].start_at.split('-')[2];
        var gt_end_year=response.data.occupied[i].end_at.split('-')[0];
        var gt_end_month=response.data.occupied[i].end_at.split('-')[1];
        var gt_end_day=response.data.occupied[i].end_at.split('-')[2];
        if(gt_start_day[0]=='0'){
            gt_start_day=gt_start_day.substring(1);
        }
        if(gt_start_month[0]=='0'){
         gt_start_month=gt_start_month.substring(1);
     }
     if(gt_end_day[0]=='0'){
        gt_end_day=gt_end_day.substring(1);
    }
    if(gt_end_month[0]=='0'){
     gt_end_month=gt_end_month.substring(1);
 }
   
     
     
    if(userIndex != undefined ){
     resourceList[userIndex].occupied.push({date:gt_start_day+'-'+gt_start_month+'-'+gt_start_year,start_at:gt_start_day+'-'+gt_start_month+'-'+gt_start_year,end_at:gt_end_day+'-'+gt_end_month+'-'+gt_end_year,member:response.data.occupied[i].member});
    }
    
     
     }
    getInitDatas();
   
    $('.lv-loader').hide()

})
.catch(function (error) {
  // handle error
  console.log(error);
})
}
function userSearch(key){
    for (var j=0; j < resourceList.length; j++) {
        if (resourceList[j].id == key) {
            return j;
        }
    }
    // alert("User search function");
}
function leaveSearch(staffId){
    for (var k=0; k < leaveSheet.length; k++) {
        if (leaveSheet[k].staff == staffId) {
          
            return leaveSheet[k].id;
        }
    }
}
function closeCancelModal(){
    $('#cancelModal').hide();
    closeConf();

}

function cancelLeave(){
    
      axios.get(url+'/api/leave-scheduler-delete/'+leaveId)
      .then(function (response) {
        // handle success
        resourceLeave=[];
        selectedDates=[];
        resourceList=[];
        reinitVal();
        getUsers();
       
       
      leaveId='';
      $('#leaveModal').hide();
      dateCounter=0;
      $('#select-counter').text(dateCounter);
      })
      .catch(function (error) {
        // handle error
        console.log(error);
      })
      closeConf();
  }
  function getLeaveId(ldate,staffid){
      for(var i=0;i<resourceList[staffid].leave.length;i++){
          if(resourceList[staffid].leave[i].date==ldate){
              return resourceList[staffid].leave[i].leave_id;
          }
      }
  }

