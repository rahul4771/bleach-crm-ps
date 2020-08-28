google.charts.load('current',{
callback: function () {
    drawChart();
    $(window).resize(drawChart);
},
'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

//googlechart
function drawChart() {
    
    if ($('#daym').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#ord_fromdate').val();
        var to = $('#ord_todate').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{
        var dom = 'Month' ;
        var from_my = $('#month1').val();
        var to_my = $('#month2').val();
        var fromdate= from_my;
        var todate= to_my;
        console.log(from_my, to_my, "monthd")
    }
    
    var dates = [];
    var subs = [];
    var apps = [];

    $.ajax({
        url: "/agent/ajax/ticketdata/",
        data: {
        'fromdate': fromdate,'todate':todate,'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
        console.log('lp')
        var quotes = [['Date', 'Tickets', 'Follow-up Cleaning']];
        var tkt_tot = 0;
        var foll_tkt = 0;

        $.each(data,function(key,value){
            var vals = value.date.split('-');
            var year = parseInt(vals[0]);
            var month = parseInt (vals[1]);
            var day = parseInt (vals[2]);
            // console.log(year,month,day)
        quotes.push([new Date(year,month-1,day),value.total,value.followup]);
            tkt_tot += parseInt(value.total);
            foll_tkt += parseInt(value.followup);
            dates.push(new Date(value.date));
            subs.push(value.total);
            apps.push(value.followup);
        });
        
        console.log(tkt_tot,foll_tkt,"war ");
        $('#total_submitted').text(tkt_tot);
        $('#total_approved').text(foll_tkt);

        var quotations = google.visualization.arrayToDataTable(quotes);

        var options = {
            chartArea : {height: '80%',},
            width:'100%',
            animation: {
            duration: 2000,
            easing: 'linear',
            startup:true
            },
            vAxis: {minValue: 0},
            legend: 'none',
            interpolateNulls: true
        };

        var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
        chart.draw(quotations, options);
        }
    });
}

var date1 = new Date();
var month = ("0" + (date1.getMonth()-1)).slice(-2);
var month2 = ("0" + (date1.getMonth())).slice(-2);
console.log(month,"lp")
var datestring = month + "/" + date1.getFullYear();
var datestring2 = month2 + "/" + date1.getFullYear();

$('#month1').val(datestring);
$('#month2').val(datestring2);

if ($('#daym').is(':checked')) {
    console.log("runnon")
    $('.set1').attr("hidden",false);
    $('.set2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.set1').attr("hidden",true);
    $('.set2').attr("hidden",false);
}

$("#ord_fromdate").change(function(){
    console.log('room');
    drawChart();   
});

$("#ord_todate").change(function(){
    console.log('room');
    drawChart();   
});

$("#month1").on("change",(function(){
    drawChart();
    console.log('room');
}));

$("#month2").on("change",(function(){
    drawChart();
    console.log('room');
}));

$("#reset_tickets").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#ord_fromdate').val(datestring2);
    $('#ord_todate').val(datestring);

    drawChart();
})

$("#daym").click(function(){
    if ($(this).is(':checked')){
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
        drawChart();
    }
    else{
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);

        // $('#month1').val(datestring2);
        // $('#month2').val(datestring);
        drawChart();

    }
})