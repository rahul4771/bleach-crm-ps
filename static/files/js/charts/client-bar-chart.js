var date1 = new Date();
date1.setDate(date1.getDate()-1);
var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

var date2 = new Date();
date2.setDate(date2.getDate()-30);
var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
console.log(datestring,datestring2)

var month = ("0" + (date1.getMonth())).slice(-2);
var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
console.log(month,"lp")
var monthstring = month + "/" + date1.getFullYear();
var monthstring2 = month2 + "/" + date1.getFullYear();

$('#client_fromdate').val(datestring2);
$('#client_todate').val(datestring);

$('#client_month1').val(monthstring);
$('#client_month2').val(monthstring2);

google.charts.load('current', {packages: ['corechart', 'bar']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic() {
    if ($('#daym').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#client_fromdate').val();
        var to = $('#client_todate').val();
  
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{
        var dom = 'Month' ;
        var from_my = $('#client_month1').val();
        var to_my = $('#client_month2').val();
        var fromdate= from_my;
        var todate= to_my;
        console.log(from_my, to_my, "monthd")
    }

    $.ajax({
        url: "/agent/ajax/clientdata/",
        data: {
        'fromdate': fromdate,'todate':todate, 'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
            var total_clients = 0;
            var clients = [['Governorate', 'Clients']];

            $.each(data,function(key,value){
                console.log(value.governorate,parseInt(value.clients),"gov")
                clients.push([value.governorate,value.clients]);
                total_clients += parseInt(value.clients)
            });

            $('#totalclients').text(total_clients);
            // console.log(data,"pop")
            console.log(clients,"lp")

            var data = google.visualization.arrayToDataTable(clients);

            var options = {
                chartArea:{height:'80%'},
                hAxis: {
                minValue: 0
                },
                width:'100%',
                height:200,
                animation:{
                    duration:1000,
                    easing:'linear',
                    startup:true
                },
                legend:'none'
            };

            var chart = new google.visualization.BarChart(document.getElementById('chart_div'));

            chart.draw(data, options);
        }
    })
    }

$("#client_fromdate").change(function(){
    console.log('room');
    drawBasic();   
});

$("#client_todate").change(function(){
    drawBasic();
    console.log('room');
});

$("#client_month1").change(function(){
    console.log('room');
    drawBasic();   
});

$("#client_month2").change(function(){
    drawBasic();
    console.log('room');
});

$("#reset_clients").click(function(){
    var date1 = new Date();
    date1.setDate(date1.getDate()-1);
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#client_fromdate').val(datestring2);
    $('#client_todate').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var datestring = month + "/" + date1.getFullYear();
    var datestring2 = month2 + "/" + date1.getFullYear();
    
    $('#client_month1').val(datestring);
    $('#client_month2').val(datestring2);
    drawBasic();
  })

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

  $("#daym").click(function(){
    if ($(this).is(':checked')){
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#client_fromdate').val(datestring2);
        $('#client_todate').val(datestring);
        drawBasic();
    }
    else{
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);

        var date1 = new Date();
        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();

        $('#client_month1').val(datestring);
        $('#client_month2').val(datestring2);
        drawBasic();

    }
})
