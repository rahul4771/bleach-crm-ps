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

        const monthNames = ["0","January", "February", "March", "April", "May", "June",
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
                // var vals2 = value.date.split('-');
                // var year2 = parseInt(vals2[0]);
                // var month2 = parseInt (vals2[1]);
                // var day2 = parseInt (vals2[2]);
                // console.log(year2,month2,day2,value.total,value.followup,"ter")
                // const d2 = new Date(year2,month2-1,day2)
                tickets2.push([monthNames[value.date],value.total,value.followup]);
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

                var tkt_date = new Date(year,month,day)
                tkt_date.setMonth(tkt_date.getMonth()-1);

            quotes.push([tkt_date,value.total,value.followup]);
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
            $('.set1').attr("hidden",true);
            $('.set2').attr("hidden",false);
            console.log("red2")
            drawBars();
        }else{
            console.log("red")
            drawLine();
            $('.set1').attr("hidden",false);
            $('.set2').attr("hidden",true);
        }
    });

    $("#month1").on("change",(function(){
        drawBars();
    }));
    
    $("#month2").on("change",(function(){
        drawBars();
    }));

    $("#ord_fromdate").change(function(){
        fromtodatecheck();
        drawLine();   
    });
    
    $("#ord_todate").change(function(){
        fromtodatecheck();
        drawLine();   
    });

    $("#reset_tickets").click(function(){
        if ($("#daym").is(':checked')){

            var date1 = new Date();
            date1.setMonth(date1.getMonth()-1);

            var date2 = new Date();

            var month = appendLeadingZeroes(date1.getMonth()+1);
            var month2 = appendLeadingZeroes(date2.getMonth()+1);

            var monthstring = month + "/" + date1.getFullYear();
            var monthstring2 = month2 + "/" + date2.getFullYear();

            $('#month1').val(monthstring);
            $('#month2').val(monthstring2);
            drawBars();
    }else{
        var date3 = new Date();
        date3.setDate(date3.getDate()-1)
        
        var datestring = appendLeadingZeroes(date3.getDate())  + "-" + appendLeadingZeroes(date3.getMonth()+1) + "-" + date3.getFullYear();

        var date4 = new Date();
        date4.setDate(date4.getDate()-30);
        
        var datestring2 = appendLeadingZeroes(date4.getDate())  + "-" + appendLeadingZeroes(date4.getMonth()+1) + "-" + date4.getFullYear();
        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
        drawLine();
    }
    });

    if ($("#daym").is(':checked')){
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);
        drawBars();
    }else{
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        drawLine();
    };
    
}

function appendLeadingZeroes(n){
    if(n <= 9){
      return "0" + n;
    }
    return n
  }

var date1 = new Date();
date1.setMonth(date1.getMonth()-1);

var date2 = new Date();

var month = appendLeadingZeroes(date1.getMonth()+1);
var month2 = appendLeadingZeroes(date2.getMonth()+1);

var monthstring = month + "/" + date1.getFullYear();
var monthstring2 = month2 + "/" + date2.getFullYear();

$('#month1').val(monthstring);
$('#month2').val(monthstring2);

var date3 = new Date();
date3.setDate(date3.getDate()-1)

var datestring = appendLeadingZeroes(date3.getDate())  + "-" + appendLeadingZeroes(date3.getMonth()+1) + "-" + date3.getFullYear();

var date4 = new Date();
date4.setDate(date4.getDate()-30);

var datestring2 = appendLeadingZeroes(date4.getDate())  + "-" + appendLeadingZeroes(date4.getMonth()+1) + "-" + date4.getFullYear();
console.log(datestring,datestring2)

$('#ord_fromdate').val(datestring2);
$('#ord_todate').val(datestring);