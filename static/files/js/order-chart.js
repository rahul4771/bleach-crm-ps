google.charts.load('current',{
callback: function () {
  drawChart();
  $(window).resize(drawChart);
},
'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

//googlechart
function drawChart() {
    
    if ($('#daym').val() == 'month') {
        var dom = 'Month' ;
        var from_my = $('#month1').val();
        var to_my = $('#month2').val();
        var fromdate= from_my;
        var todate= to_my;
        console.log(from_my, to_my, "monthd")
    }else{
        var dom = 'Date' ;
        var fromd = $('#ord_fromdate').val();
        var to = $('#ord_todate').val();
  
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }
    
    var dates = [];
    var subs = [];
    var apps = [];

    $.ajax({
        url: '/order-data/quotation_data',
        data: {
        'fromdate': fromdate,'todate':todate,'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
        console.log('lp')
        var quotes = [['Date', 'Submitted', 'Approved']];
        var sub_sum = 0;
        var app_sum = 0;

        $.each(data,function(key,value){
            var vals = value.date.split('-');
            var year = parseInt(vals[0]);
            var month = parseInt (vals[1]);
            var day = parseInt (vals[2]);
            // console.log(year,month,day)
        quotes.push([new Date(year,month-1,day),value.sub_qt,value.app_qt]);
            sub_sum += parseInt(value.sub_qt);
            app_sum += parseInt(value.app_qt);
            dates.push(new Date(value.date));
            subs.push(value.sub_qt);
            apps.push(value.app_qt);
        });
        
        console.log(sub_sum,app_sum,"war ");
        $('#total_submitted').text(sub_sum);
        $('#total_approved').text(app_sum);

        var quotations = google.visualization.arrayToDataTable(quotes);

        var options = {
            chartArea : {height: '80%',},
            width:500,
            animation: {
            duration: 2000,
            easing: 'linear',
            startup:true
            },
            vAxis: {minValue: 0},
            legend: 'none'
        };

        var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
        chart.draw(quotations, options);
        }
    });
}

var months = [ "January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December" ];

var date1 = new Date();
var month = date1.getMonth();
var month2 = date1.getMonth()-1;
var selectedMonthName = months[month];
var selectedMonthName2 = months[month2];
console.log(selectedMonthName,"lp")
var datestring = selectedMonthName + " " + date1.getFullYear();
var datestring2 = selectedMonthName2 + " " + date1.getFullYear();
$('#month1').val(datestring2);
$('#month2').val(datestring);

$('#example7').calendar({
    type: 'month'
});

$('#example8').calendar({
    type: 'month'
});

if ($('#daym').val() == 'month'){
    console.log("runn")
    $('.set1').attr("hidden",true);
    $('.set2').attr("hidden",false);
}
else{
    console.log("runnon")
    $('.set1').attr("hidden",false);
    $('.set2').attr("hidden",true);
}

$("#ord_fromdate").change(function(){
    console.log('room');
    drawChart();   
});

$("#ord_todate").change(function(){
    console.log('room');
    drawChart();   
});

$("#mnt_btn").on("click",function(){
    console.log($("#month1").val(),$("#month2").val(),'room');
    drawChart();   
});

$("#month1").change(function(){
    drawChart();
    console.log('room');
});

$("#month2").change(function(){
    drawChart();
    console.log('room');
});

$("#reset").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "/" + (date2.getMonth()+1) + "/" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#from').val(datestring2);
    $('#to').val(datestring);

    drawChart();
})

$("#daym").change(function(){
    if ($(this).val() == 'month'){
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);

        // $('#month1').val(datestring2);
        // $('#month2').val(datestring);
        drawChart();
    }
    else{
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
        drawChart();

    }
})