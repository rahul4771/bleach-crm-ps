




$(".lv-result-box").hide();
$(".lv-conf").hide();
var modalBox=false;
var DateTime = luxon.DateTime;

var selectedId = [];
/*console.log("testing :"+DateTime.fromObject({ weekYear: 2016, weekNumber: 2, weekday: 3 }).toISODate());
console.log("testing :"+DateTime.local(2016, 1).daysInMonth);
console.log("testing :"+DateTime.local(2021, 02, 19).weekdayShort);*/
var days=['M','T','W','T','F','S','S'];
var currentMonth = DateTime.local().month; //CURRENT MONTH
var currentYear=DateTime.local().year;   //CURRENT YEAR
var currentDay=DateTime.local(2017, 10, 30).weekday; //CURRENT DAY

$('#lv-month-select').text(DateTime.local().monthLong+' '+ DateTime.local().year);
var resources=['Amanediel','Michael','Eve'];
var selectedDates=[];
var resourceList=[
    {
        name:'Amanediel',
        leave:[
            {
                date:'3-2-2021',
                type:'Annual Leave'
            },
            {
                date:'8-2-2021',
                type:'Weekly Off'
            }
        ]
    },
    {
        name:'Michael',
        leave:[]
    },
    {
        name:'Eve',
        leave:[
            {
                date:'12-3-2021',
                type:'Sick Leave'
            }
        ]
    },
    {
        name:'Chloe',
        leave:[
            {
                date:'14-1-2021',
                type:'Sick Leave'
            }
        ]
    },
    {
        name:'Ella Lopez',
        leave:[
            {
                date:'26-2-2021',
                type:'Sick Leave'
            },
            {
                date:'28-2-2021',
                type:'Sick Leave'
            }
        ]
    },
    {
        name:'Daniel',
        leave:[
            {
                date:'12-3-2021',
                type:'Sick Leave'
            }
        ]
    },
    {
        name:'Charlie',
        leave:[
            {
                date:'18-2-2021',
                type:'Sick Leave'
            }
        ]
    },
    {
        name:'Trixie',
        leave:[
            {
                date:'7-2-2021',
                type:'Maternity Leave'
            },
            {
                date:'12-3-2021',
                type:'Annual Leave'
            }
        ]
    },
    {
        name:'Linda',
        leave:[
            {
                date:'19-2-2021',
                type:'Annual Leave'
            }
        ]
    },
    {
        name:'Maze',
        leave:[
            {
                date:'22-2-2021',
                type:'Weekly Off'
            }
        ]
    }

   
   
];
for(var i=0;i<resourceList.length;i++){
    selectedDates.push({name:'',dates:[]})
}

var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;
var found=false;
//var noOfWeek=noOfDays/7;
for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;

  
    $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');
}
console.log("testing :"+noOfDays);
for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    $('#lv-body-head').append('<tr class="lv-rows" id="row-'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text">'+resourceList[j].leave.length+'</span></div> <img src="images/profile-picblack.jpg" align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">Sales</div></div></td></tr>');
   
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        if(resourceList[j].leave.length>0)
        {
            for(var rs=0;rs<resourceList[j].leave.length;rs++){
               
                if(resourceList[j].leave[rs].date==today){
                    if(resourceList[j].leave[rs].date==today){
                        if(resourceList[j].leave[rs].type=='Annual Leave'){
                         $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                        }
                        else{
                            if(resourceList[j].leave[rs].type=='Weekly Off'){
                                $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
            
                               }
                               else{
                                if(resourceList[j].leave[rs].type=='Maternity/Paternity'){
                                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-maternity" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                                   }
                                   else{
                                    if(resourceList[j].leave[rs].type=='Sick Leave'){
                                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-sick" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                    
                                       }
                                   }
                               }
                        }
                       
                       
                       
     
                        found=true;
                     }
                }
              
                
            }
            
           

        }
        if(found==false)
        {
            $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

        }
      
    
    }

}
function nextMonth(){
    currentMonth=currentMonth+1;
    if(currentMonth>12){
        currentMonth=1;
        currentYear=currentYear+1;
       
    }
    $('#lv-month-select').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
    reCalc();

}
function previousMonth(){
    currentMonth=currentMonth-1;
    if(currentMonth<1){
        currentMonth=12;
        currentYear=currentYear-1;
       
    }
    $('#lv-month-select').text(DateTime.local(currentYear,currentMonth).monthLong+' '+ currentYear);
   
    reCalc();
    
}
function reCalc(){
    $('.day-head').remove();
    $('.lv-rows').remove();
    var noOfDays = DateTime.local(2021, currentMonth).daysInMonth;
//var noOfWeek=noOfDays/7;
for (var k=1;k<=noOfDays;k++){
    var day=DateTime.local(currentYear, currentMonth, k).weekday-1;

  
    $('#lv-head-'+k).after('<th class="noBorder day-head" id="lv-head-'+(k+1)+'"> <div class="lv-day">'+DateTime.local(currentYear, currentMonth, k).weekdayShort.substring(0,1)+'</div></th>');
}
console.log("resource liST IS"+JSON.stringify(resourceList));
for (var j=0;j<resourceList.length;j++){
    var rsid=j+1;
    $('#lv-body-head').append('<tr class="lv-rows" id="row-'+rsid+'"><td class="noBorder"> <div class="lv-resource d-flex "> <div class="lv-counter"><span class="counter-text">'+resourceList[j].leave.length+'</span></div> <img src="images/profile-picblack.jpg" align="absmiddle" class="profile-icon"> <div class="resource-profile"><div class="resource-name text-primary">'+resourceList[j].name+'</div><div class="lv-position">Sales</div></div></td></tr>');
    for(var i=1;i<=noOfDays;i++){
        found=false;
        var today = i.toString()+'-'+currentMonth.toString()+'-'+currentYear.toString();
        if(resourceList[j].leave.length>0)
        {
            for(var rs=0;rs<resourceList[j].leave.length;rs++){
               
                if(resourceList[j].leave[rs].date==today){
                   if(resourceList[j].leave[rs].type=='Annual Leave'){
                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-annual" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                   }
                   else{
                   if(resourceList[j].leave[rs].type=='Weekly Off'){
                    $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-weekly" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

                   }
                   else{
                    if(resourceList[j].leave[rs].type=='Maternity/Paternity'){
                        $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-maternity" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
                       }
                       else{
                        if(resourceList[j].leave[rs].type=='Sick Leave'){
                            $('#row-'+rsid).append('<td class="noBorder text-center lv-date"  onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date lv-sick" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');
        
                           }
                       }
                   }
                }
                   
                   

                   found=true;
                }
              
                
            }
            
           

        }
        if(found==false)
        {
            $('#row-'+rsid).append('<td class="noBorder text-center lv-date" onclick="selectDay(this)" id="lv-day-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'"'+'><div class="lv-date" id="lv-date-'+j+'-'+i+'-'+currentMonth+'-'+currentYear+'">'+i+'</div></td>');

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
    seletedDates=[];
    for(var i=0;i<resourceList.length;i++){
        selectedDates.push({name:'',dates:[]});
    }

}
function selectDay(el){
    var dayId=$(el).attr('id');
    console.log("my id is "+dayId);
    var userId=dayId.split('-')[2];
    var user=resourceList[userId].name;
    
    selectedDates[userId].name=user;
    if($('#'+dayId).find('.lv-date').hasClass('lv-annual')){
        $("#myModal").modal({backdrop: false});
        $('.modal-title').text('Annual Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-annual-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-sick')){

        $("#myModal").modal({backdrop: false});

        $('.modal-title').text('Sick Leave');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-sick-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-maternity')){
        $("#myModal").modal({backdrop: false});
        $('.modal-title').text('Maternity/Paternity Leave');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-weekly-text');
        $('.modal-title').addClass('lv-maternity-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
    }
    if($('#'+dayId).find('.lv-date').hasClass('lv-weekly')){
        $("#myModal").modal({backdrop: false});
        $('.modal-title').text('Weekly Off');
        $('.modal-title').removeClass('lv-sick-text');
        $('.modal-title').removeClass('lv-annual-text');
        $('.modal-title').removeClass('lv-maternity-text');
        $('.modal-title').addClass('lv-weekly-text');
        $('.modal-date').text($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        $('.modal-resource').text(user);
    }
    else{
    if($('#'+dayId).find('.lv-date').hasClass('lv-selected-date')||$('#'+dayId).find('.lv-date').hasClass('lv-annual')||$('#'+dayId).find('.lv-date').hasClass('lv-weekly')||$('#'+dayId).find('.lv-date').hasClass('lv-maternity')||$('#'+dayId).find('.lv-date').hasClass('lv-sick')){
        $('#'+dayId).find('.lv-date').removeClass('lv-selected-date');
        var index = selectedId.indexOf(dayId);
        var selectedIndex=selectedDates[userId].dates.indexOf($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString());
        if (index !== -1) {
                selectedId.splice(index, 1);
              //  selectedData.dates.splice(selectedIndex,1);
                selectedDates[userId].dates.splice(selectedIndex,1);
        }
     
    }
    else{
        $('#'+dayId).find('.lv-date').addClass('lv-selected-date');
        selectedId.push(dayId);
       // selectedData.dates.push($('#'+dayId).find('.lv-date').text().toString()+'-'+currentMonth.toString()+'-'+currentYear.toString())
        selectedDates[userId].dates.push($('#'+dayId).find('.lv-date').text()+'-'+currentMonth.toString()+'-'+currentYear.toString());
    }
}
    console.log("selected dates are "+ JSON.stringify(selectedDates));
}
function openForm(){
  
    $(".lv-result-box").show();
  
}
function closeForm(){
  
    $(".lv-result-box").hide();
  
}
function applyLeave(){
    
    for(var i=0;i<selectedDates.length;i++){
        for (var j=0;j<selectedDates[i].dates.length;j++){
            var leaveData={
                type:$("#lv-result-content").text(),
                date:selectedDates[i].dates[j]
            }
            resourceList[i].leave.push(leaveData);
        }
    }
    console.log("val is"+JSON.stringify( resourceList));
    selectedDates=[];
    reCalc();
    reinitVal();
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
function cancelLeave(){

}

