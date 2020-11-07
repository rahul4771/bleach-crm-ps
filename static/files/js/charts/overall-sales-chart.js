google.load('visualization', '1.0', {
    'packages': ['corechart']
});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initialize);

function initialize() {

    var chart = new google.visualization.ChartWrapper({
        containerId: 'chart_div2'
    });

    var data = [];

    var options = {
        chartArea : {height: '80%',},
        width: '100%',
        curveType: 'function',
        vAxis: {
            minValue: 0,
            viewWindow: {min: 0}
        },
        animation: {
            duration: 1000,
            easing: 'out'
        },
        legend:{position:'none'},
        lineWidth: 5,
    };
    
    chart.setOptions(options);
    
    function drawBars() {
        var dom2 = 'Month' ;
        var month_1 = $('#sales_curve_month1').val();
        var month_2 = $('#sales_curve_month2').val();

        console.log(month_1, month_2, "monthd2")

        const monthNames = ["0","January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
        ];

        $.ajax({
            url: "/bleach_admin/ajax/sales-curve-data/",
            data: {
            'fromdate': month_1,'todate':month_2,'dom':dom2
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_month) {
            var sales = [['Month', 'Sales']];
            var sale_sum = 0;
            var total_sum = 0;

            if(data_month.length > 0){
                $.each(data_month,function(key,value){
                    console.log(value.date,"uio")
                    // var vals = value.date.split('-');
                    // var year = parseInt(vals[0]);
                    // var month = parseInt (vals[1]);
                    // var day = parseInt (vals[2]);
                    // const d2 = new Date(year,month-1,day);
                sales.push([monthNames[value.date],value.amount]);
                    sale_sum += parseInt(value.amount);
                    total_sum += parseInt(value.total);
                });
            }else{
                sales.push(['',0]);
                sale_sum = 0;
                total_sum = 0;
            }
            console.log(sales,"sls")
            $('#total_sales').text(sale_sum);
            $('#total_orders').text(total_sum);


            data[0] = new google.visualization.arrayToDataTable(sales);

            chart.setChartType('ColumnChart');
            chart.setDataTable(data[0]);
            chart.draw();
        }
        });
    }

    function drawArea() {

        var dom = 'Date' ;
        var fromd = $('#sales_curve_date1').val();
        var to = $('#sales_curve_date2').val();

        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')

        $.ajax({
            url: "/bleach_admin/ajax/sales-curve-data/",
            data: {
            'fromdate': fromdate,'todate':todate,'dom':dom
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_date) {
            var sales = [['Date', 'Sales']];
            var sale_sum = 0;
            var total_sum = 0;
            
            if(data_date.length > 0){
                $.each(data_date,function(key,value){
                    console.log(value.date,"uio")
                    var vals = value.date.split('-');
                    var year = parseInt(vals[0]);
                    var month = parseInt (vals[1]);
                    var day = parseInt (vals[2]);
                    // console.log(year,month,day)

                    var os_date = new Date(year,month,day)
                    os_date.setMonth(os_date.getMonth()-1);

                sales.push([os_date,value.amount]);
                    sale_sum += parseInt(value.amount);
                    total_sum += parseInt(value.total);
                });
            }else{
                sales.push(['',0]);
                sale_sum = 0;
                total_sum = 0;
            }
            console.log(sales,"sls")
            $('#total_sales').text(sale_sum);
            $('#total_orders').text(total_sum);

            data[1] = new google.visualization.arrayToDataTable(sales);

            chart.setChartType('LineChart');
            chart.setDataTable(data[1]);
            chart.draw();
        }
        });
    }
    
    $("#daymonth_sales").click(function(){
        if ($(this).is(':checked')){
            $('.saleset1').attr("hidden",true);
            $('.saleset2').attr("hidden",false);
            console.log("red2")
            drawBars();
        }else{
            console.log("red")
            drawArea();
            $('.saleset1').attr("hidden",false);
            $('.saleset2').attr("hidden",true);
        }
    });

    $("#sales_curve_month1").on("change",(function(){
        drawBars();
    }));
    
    $("#sales_curve_month2").on("change",(function(){
        drawBars();
    }));

    $("#sales_curve_date1").change(function(){
        fromtodatecheck();
        drawArea();   
    });
    
    $("#sales_curve_date2").change(function(){
        fromtodatecheck();
        drawArea();   
    });

    $("#reset_sales_curve").click(function(){
        if ($("#daymonth_sales").is(':checked')){
        var date1 = new Date();

        var date2 = new Date();
        date2.setMonth(date2.getMonth()+1);

        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date2.getMonth())).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date2.getFullYear();

        $('#sales_curve_month1').val(datestring);
        $('#sales_curve_month2').val(datestring2);
        drawBars();
    }else{
        var date1 = new Date();

        date1.setDate(date1.getDate()-1)
        date1.setMonth(date1.getMonth()+1)
        var datestring = ("0" + (date1.getDate())).slice(-2)  + "-" + ("0" + (date1.getMonth())).slice(-2) + "-" + date1.getFullYear();
        
        var date2 = new Date();
        date2.setDate(date2.getDate()-30);
        date2.setMonth(date2.getMonth()+1)
        var datestring2 = ("0" + (date2.getDate())).slice(-2)  + "-" + ("0" + (date2.getMonth())).slice(-2) + "-" + date2.getFullYear();
        console.log(datestring,datestring2)
    
        $('#sales_curve_date1').val(datestring2);
        $('#sales_curve_date2').val(datestring);
    
        drawArea();
    }
    });

    if ($("#daymonth_sales").is(':checked')){
        $('.saleset1').attr("hidden",true);
        $('.saleset2').attr("hidden",false);
        drawBars();
    }else{
        $('.saleset1').attr("hidden",false);
        $('.saleset2').attr("hidden",true);
        drawArea();
    };
    
}

var date1 = new Date();

var date2 = new Date();
date2.setMonth(date2.getMonth()+1);

var month = ("0" + (date1.getMonth())).slice(-2);
var month2 = ("0" + (date2.getMonth())).slice(-2);
console.log(month,"lp")
var datestring = month + "/" + date1.getFullYear();
var datestring2 = month2 + "/" + date2.getFullYear();

$('#sales_curve_month1').val(datestring);
$('#sales_curve_month2').val(datestring2);

var date3 = new Date();

date3.setDate(date3.getDate()-1)
date3.setMonth(date3.getMonth()+1)
var datestring = ("0" + (date3.getDate())).slice(-2)  + "-" + ("0" + (date3.getMonth())).slice(-2) + "-" + date3.getFullYear();

var date4 = new Date();
date4.setDate(date4.getDate()-30);
date4.setMonth(date4.getMonth()+1)
var datestring2 = ("0" + (date4.getDate())).slice(-2)  + "-" + ("0" + (date4.getMonth())).slice(-2) + "-" + date4.getFullYear();
console.log(datestring,datestring2,"dats")

$('#sales_curve_date1').val(datestring2);
$('#sales_curve_date2').val(datestring);