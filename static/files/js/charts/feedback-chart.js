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
            url: "/agent/ajax/feedbackdata/",
            data: {
            'fromdate': month_1,'todate':month_2,'dom':dom2
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_month) {
            var quotations = [['Date', 'Avg. Rating']];
            var tot_ratings = 0;
            var count = 0;
            console.log(data_month.length,"dlen")
            if(data_month.length > 0){
            $.each(data_month,function(key,value){

                var vals = value.date.split('-');
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                console.log(year,month,day,parseFloat((value.avg_rating).toFixed(2)),"ter")

                const d2 = new Date(year,month-1,day)
                quotations.push([monthNames[d2.getMonth()],parseFloat((value.avg_rating).toFixed(2))]);
                tot_ratings += parseFloat((value.avg_rating).toFixed(2));
                count++ ;
            });
            }else{
                quotations.push(['',0]);
            }

            var avg_total_rating = parseFloat(tot_ratings/parseInt(count)).toFixed(2);
            if (isNaN(avg_total_rating)) avg_total_rating = 0.00; 
            console.log(avg_total_rating,"war2 ");
            $('#total_submitted').text(avg_total_rating);


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
            url: "/agent/ajax/feedbackdata/",
            data: {
            'fromdate': fromdate,'todate':todate,'dom':dom
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_date) {
            var quotations = [['Date', 'Rating']];
            var tot_ratings = 0;
            var count = 0;
            
            if(data_date.length > 0){
            $.each(data_date,function(key,value){
                var vals = value.date.split('-');
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                console.log(year,month,day,value.avg_rating,"ter")

            quotations.push([new Date(year,month-1,day),parseFloat((value.avg_rating).toFixed(2))]);
                tot_ratings += parseFloat((value.avg_rating).toFixed(2));
                count++ ;
            });
            }else{
                quotations.push(['',0]);
            }
            console.log(tot_ratings,"war ");
            var avg_total_rating = parseFloat(tot_ratings/parseInt(count)).toFixed(2);
            $('#total_submitted').text(avg_total_rating);

            data[1] = new google.visualization.arrayToDataTable(quotations);

            chart.setChartType('AreaChart');
            chart.setDataTable(data[1]);
            chart.draw();
        }
        });
    }
    
    $("#daymonthtoggle").click(function(){
        if ($(this).is(':checked')){
            console.log("red")
            drawArea();
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
        drawArea();   
    });
    
    $("#ord_todate").change(function(){
        drawArea();   
    });

    $("#reset_feedbacks").click(function(){
        if ($("#daymonthtoggle").is(':checked')){
        var date1 = new Date();
        var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();
    
        var date2 = new Date();
        date2.setDate(date2.getDate()-30);
        var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
        console.log(datestring,datestring2)
    
        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
    
        drawArea();
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

    if ($("#daymonthtoggle").is(':checked')){
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        drawArea();
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