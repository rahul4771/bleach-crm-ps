google.load('visualization', '1.0', {
    'packages': ['corechart']
});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initialize);

function initialize() {

    var chart = new google.visualization.ChartWrapper({
        containerId: 'chart_div'
    });

    var data = [];

    var options = {
        chartArea : {height: '80%',},
        width: '100%',
        vAxis: {
            minValue: 0,
        },
        animation: {
            duration: 1000,
            easing: 'out'
        },
        legend:{position:'none'}
    };
    
    chart.setOptions(options);
    
    function drawBars() {
        var dom2 = 'Month' ;
        var month_1 = $('#month1').val();
        var month_2 = $('#month2').val();

        console.log(month_1, month_2, "monthd2")

        const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
        ];

        $.ajax({
            url: "/agent/ajax/ticketdata/",
            data: {
            'fromdate': month_1,'todate':month_2,'dom':dom2
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_month) {
            var tickets2 = [['Month', 'Tickets', 'Follow-up Cleaning']];
            var tkt_tot2 = 0;
            var foll_tkt2 = 0;
            if(data_month.length > 0){
            $.each(data_month,function(key,value){
                var vals2 = value.date.split('-');
                var year2 = parseInt(vals2[0]);
                var month2 = parseInt (vals2[1]);
                var day2 = parseInt (vals2[2]);
                console.log(year2,month2,day2,value.total,value.followup,"ter")
                const d2 = new Date(year2,month2-1,day2)
                tickets2.push([monthNames[d2.getMonth()],value.total,value.followup]);
                tkt_tot2 += parseInt(value.total);
                foll_tkt2 += parseInt(value.followup);
            });
            }else{
                tickets2.push(['',0,0]);
            }
            console.log(tkt_tot2,foll_tkt2,"war2 ");
            $('#total_submitted').text(tkt_tot2);
            $('#total_approved').text(foll_tkt2);


            data[0] = new google.visualization.arrayToDataTable(tickets2);

            chart.setChartType('ColumnChart');
            chart.setDataTable(data[0]);
            chart.draw();
        }
        });
    }

    function drawLine() {

        var dom = 'Date' ;
        var fromd = $('#ord_fromdate').val();
        var to = $('#ord_todate').val();

        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')

        $.ajax({
            url: "/agent/ajax/ticketdata/",
            data: {
            'fromdate': fromdate,'todate':todate,'dom':dom
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_date) {
            var quotes = [['Date', 'Tickets', 'Follow-up Cleaning']];
            var tkt_tot = 0;
            var foll_tkt = 0;
            if(data_date.length > 0){
            $.each(data_date,function(key,value){
                var vals = value.date.split('-');
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                console.log(year,month,day,value.total,value.followup,"ter")
            quotes.push([new Date(year,month-1,day),value.total,value.followup]);
                tkt_tot += parseInt(value.total);
                foll_tkt += parseInt(value.followup);
            });
            }else{
                quotes.push(['',0,0]);
            }
            console.log(tkt_tot,foll_tkt,"war ");
            $('#total_submitted').text(tkt_tot);
            $('#total_approved').text(foll_tkt);

            data[1] = new google.visualization.arrayToDataTable(quotes);

            chart.setChartType('AreaChart');
            chart.setDataTable(data[1]);
            chart.draw();
        }
        });
    }
    
    $("#daym").click(function(){
        if ($(this).is(':checked')){
            console.log("red")
            drawLine();
            $('.set1').attr("hidden",false);
            $('.set2').attr("hidden",true);
        }else{
            $('.set1').attr("hidden",true);
            $('.set2').attr("hidden",false);
            console.log("red2")
            drawBars();
        }
    });

    $("#month1").on("change",(function(){
        drawBars();
    }));
    
    $("#month2").on("change",(function(){
        drawBars();
    }));

    $("#ord_fromdate").change(function(){
        drawLine();   
    });
    
    $("#ord_todate").change(function(){
        drawLine();   
    });

    $("#reset_tickets").click(function(){
        if ($("#daym").is(':checked')){
        var date1 = new Date();
        var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();
    
        var date2 = new Date();
        date2.setDate(date2.getDate()-30);
        var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
        console.log(datestring,datestring2)
    
        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
    
        drawLine();
    }else{
        var date1 = new Date();
        var month = ("0" + (date1.getMonth()-1)).slice(-2);
        var month2 = ("0" + (date1.getMonth())).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();

        $('#month1').val(datestring);
        $('#month2').val(datestring2);
        drawBars();
    }
    });

    if ($("#daym").is(':checked')){
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        drawLine();
    }else{
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);
        drawBars();
    };
    
}

var date1 = new Date();
var month = ("0" + (date1.getMonth()-1)).slice(-2);
var month2 = ("0" + (date1.getMonth())).slice(-2);
console.log(month,"lp")
var datestring = month + "/" + date1.getFullYear();
var datestring2 = month2 + "/" + date1.getFullYear();

$('#month1').val(datestring);
$('#month2').val(datestring2);

var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

var date2 = new Date();
date2.setDate(date2.getDate()-30);
var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
console.log(datestring,datestring2)

$('#ord_fromdate').val(datestring2);
$('#ord_todate').val(datestring);