google.load('visualization', '1.0', {
    'packages': ['corechart']
});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initialize);

function initialize() {

    var chart = new google.visualization.ChartWrapper({
        containerId: 'chart_payment'
    });

    var data = [];

    var options = {
        chartArea : {height: '80%',},
        width: '100%',
        vAxis: {
            minValue: 0,
            format: '#'
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

        const monthNames = ["","January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
        ];

        $.ajax({
            url: "/bleach_admin/ajax/payment-data/",
            data: {
            'fromdate': month_1,'todate':month_2,'dom':dom2
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_month) {
            var quotations = [['Month', 'Paid']];
            var submitted_total_month = 0;
            //var approved_total_month = 0;

            if(data_month.length > 0){
            $.each(data_month,function(key,value){
            
                // var vals = value.date.split('-');
                // var year = parseInt(vals[0]);
                // var month = parseInt (vals[1]);
                // var day = parseInt (vals[2]);
                // console.log(year,month,day,value.submitted_qt,value.approved_qt,"ter")

                // const d2 = new Date(year,month-1,day)
                quotations.push([monthNames[value.date],value.total]);
                submitted_total_month += parseInt(value.total);
                //approved_total_month += parseInt(value.pending);
            });
            }else{
                quotations.push(['',0]);
            }

            console.log(submitted_total_month,"war2 ");
            $('#total_submitted').text(submitted_total_month);
            //$('#total_approved').text(approved_total_month);


            data[0] = new google.visualization.arrayToDataTable(quotations);

            chart.setChartType('ColumnChart');
            chart.setDataTable(data[0]);
            chart.draw();
        }
        });
    }

    function drawArea() {

        var dom = 'Date' ;
        var fromd = $('#ord_fromdate').val();
        var to = $('#ord_todate').val();

        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')

        $.ajax({
            url: "/bleach_admin/ajax/payment-data/",
            data: {
            'fromdate': fromdate,'todate':todate,'dom':dom
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_date) {
            var quotations = [['Date', 'Paid']];
            var submitted_total = 0;
            //var approved_total = 0;

            if(data_date.length > 0){
            $.each(data_date,function(key,value){
                var vals = value.date.split('-');
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                console.log(year,month,day,value.total,"ter")

                var payment_date = new Date(value.date+"Z")
                //payment_date.setMonth(payment_date.getMonth()-1);

            quotations.push([payment_date,value.total]);
                submitted_total += parseInt(value.total);
                //approved_total += parseInt(value.pending);
            });
            }else{
                quotations.push(['',0]);
            }
            console.log(submitted_total,"war ");
            $('#total_submitted').text(submitted_total);
            //$('#total_approved').text(approved_total);

            data[1] = new google.visualization.arrayToDataTable(quotations);

            chart.setChartType('AreaChart');
            chart.setDataTable(data[1]);
            chart.draw();
        }
        });
    }
    
    $("#daymonthtoggle").click(function(){
        if ($(this).is(':checked')){
            $('.set1').attr("hidden",true);
            $('.set2').attr("hidden",false);
            console.log("red2")
            drawBars();
        }else{
            console.log("red")
            drawArea();
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
        drawArea();   
    });
    
    $("#ord_todate").change(function(){
        fromtodatecheck();
        drawArea();   
    });

    $("#reset_orders").click(function(){
        if ($("#daymonthtoggle").is(':checked')){
            var date1 = new Date();
            date1.setMonth(date1.getMonth()-1);

            var date2 = new Date();

            var month = appendLeadingZeroes(date1.getMonth()+1);
            var month2 = appendLeadingZeroes(date2.getMonth()+1);
            console.log(month,"lp")
            var datestring = month + "/" + date1.getFullYear();
            var datestring2 = month2 + "/" + date2.getFullYear();

            $('#month1').val(datestring);
            $('#month2').val(datestring2);
            drawBars();
        
    }else{
        var date3 = new Date();
        date3.setDate(date3.getDate()-1)

        var datestring = appendLeadingZeroes(date3.getDate())  + "-" + appendLeadingZeroes(date3.getMonth()+1) + "-" + date3.getFullYear();

        var date4 = new Date();
        date4.setDate(date4.getDate()-30);
        
        var datestring2 = appendLeadingZeroes(date4.getDate())  + "-" + appendLeadingZeroes(date4.getMonth()+1) + "-" + date4.getFullYear();

        console.log(datestring,datestring2)

        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
    
        drawArea();
    }
    });

    if ($("#daymonthtoggle").is(':checked')){
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);
        drawBars();
    }else{
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        drawArea();
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