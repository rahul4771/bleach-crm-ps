var date1 = new Date();
date1.setDate(date1.getDate()-1);
var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

var date2 = new Date();
date2.setDate(date2.getDate()-30);
var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
console.log(datestring,datestring2)

$('#client_fromdate').val(datestring2);
$('#client_todate').val(datestring);

google.charts.load('current', {packages: ['corechart', 'bar']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic() {
    console.log("run")
    var fromd = $('#client_fromdate').val();
    var to = $('#client_todate').val();
    
    var fromdate= fromd.split("-").reverse().join("-");
    var todate= to.split("-").reverse().join("-");
    console.log(fromdate,todate,'pp')

    $.ajax({
        url: "/agent/ajax/clientdata/",
        data: {
        'fromdate': fromdate,'todate':todate
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
                chartArea:{height:'85%'},
                hAxis: {
                minValue: 0
                },
                width:500,
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

$("#reset").click(function(){
    var date1 = new Date();
    date1.setDate(date1.getDate()-1);
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#from').val(datestring2);
    $('#to').val(datestring);

    drawBasic();
  })
