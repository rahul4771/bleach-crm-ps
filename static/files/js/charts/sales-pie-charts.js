//donut chart
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawChart);
function drawChart() {
    var date1 = new Date();
    var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    $('#pfrom').val(datestring2);
    $('#pto').val(datestring);

    var fromd = $('#pfrom').val();
    var to = $('#pto').val();
    console.log(fromd, to,"lol")
    var fromdate= fromd.split("-").reverse().join("-");
    var todate= to.split("-").reverse().join("-");
    console.log(fromdate,todate,'pp')

    $.ajax({
        url: '/bleach_admin/ajax/sales-data/',
        data: {
        // 'fromdate': fromdate,'todate':todate
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {

            var total_sales = 0;
            var cid = 1;
            var location_sales = [['Location', 'Sales']];

        $.each(data,function(key,value){
            console.log(value.gov,parseInt(value.clients),"gov")
            location_sales.push([value.location,value.count]);
            total_sales += parseInt(value.count)
        });

        $('#clint2').text(total_sales);
        // console.log(data,"pop")
        console.log(total_sales,"tc")

        $.each(data,function(key,value){
           var percent = ((parseInt(value.count)*parseInt(100))/parseInt(total_sales));
           $('#c'+ cid++ +'').text(parseFloat(percent).toFixed(2));
        })

        var data = google.visualization.arrayToDataTable(location_sales);

        var options = {
            chartArea : {height: '80%',},
            width:300,
            title: "",
            pieHole: 0.4,
            animation: {
                duration:1000,
                easing:'out',
                startup: true
            },
            legend: 'none'
        };

        var chart = new google.visualization.PieChart(document.getElementById('donutchart1'));
        chart.draw(data, options);
        // initial value
        var percent = 0;
        // start the animation loop
        var handler = setInterval(function(){
            // values increment
            percent += 1;
            // apply new values
            data.setValue(0, 1, percent);
            data.setValue(1, 1, 100 - percent);
            // update the pie
            chart.draw(data, options);
            // check if we have reached the desired value
            if (percent > 74)
                // stop the loop
                clearInterval(handler);
        }, 30);

            }
    })
}

$("#pfrom").change(function(){
    console.log('room');
    drawChart(); 
});

$("#pto").change(function(){
    console.log('room');
    drawChart();   
});

//donut chart2
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawChart2);
function drawChart2() {
    console.log("rom")
    // var date1 = new Date();
    // var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    // var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    // $('#cln_from').val(datestring2);
    // $('#cln_to').val(datestring);

    // var fromd = $('#cln_from').val();
    // var to = $('#cln_to').val();
    // console.log(fromd, to,"lol")
    // var fromdate= fromd.split("-").reverse().join("-");
    // var todate= to.split("-").reverse().join("-");
    // console.log(fromdate,todate,'pp')

    $.ajax({
        url: '/bleach_admin/ajax/sales-data2/',
        data: {
        // 'fromdate': fromdate,'todate':todate
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {

            var total_cleaningtype_sales = 0;
            var clean_id = 1;
            var cleaningtype_sales = [['Cleaning Type', 'Sales']];

        $.each(data,function(key,value){
            console.log(value.cleaning_type,parseInt(value.count),"gov")
            cleaningtype_sales.push([value.cleaning_type,value.count]);
            total_cleaningtype_sales += parseInt(value.count)
        });

        // $('#clint2').text(total_sales);
        // console.log(data,"pop")
        console.log(total_cleaningtype_sales,"tc")

        $.each(data,function(key,value){
           var percent = ((parseInt(value.count)*parseInt(100))/parseInt(total_cleaningtype_sales));
           $('#c'+ clean_id++ +'').text(parseFloat(percent).toFixed(2));
        })

        var data = google.visualization.arrayToDataTable(cleaningtype_sales);

        var options = {
            chartArea : {height: '80%',},
            width:300,
            title: "",
            pieHole: 0.4,
            animation: {
                duration:1000,
                easing:'out',
                startup: true
            },
            legend: 'none'
        };

        var chart = new google.visualization.PieChart(document.getElementById('donutchart2'));
        chart.draw(data, options);
        // initial value
        var percent = 0;
        // start the animation loop
        var handler = setInterval(function(){
            // values increment
            percent += 1;
            // apply new values
            data.setValue(0, 1, percent);
            data.setValue(1, 1, 100 - percent);
            // update the pie
            chart.draw(data, options);
            // check if we have reached the desired value
            if (percent > 74)
                // stop the loop
                clearInterval(handler);
        }, 30);

            }
    })
}

$("#cln_from").change(function(){
    console.log('room');
    drawChart2(); 
});

$("#cln_to").change(function(){
    console.log('room');
    drawChart2();   
});

//donut chart3
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawChart3);
function drawChart3() {
    console.log("rom")
    // var date1 = new Date();
    // var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    // var datestring2 = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    // $('#cln_from').val(datestring2);
    // $('#cln_to').val(datestring);

    // var fromd = $('#cln_from').val();
    // var to = $('#cln_to').val();
    // console.log(fromd, to,"lol")
    // var fromdate= fromd.split("-").reverse().join("-");
    // var todate= to.split("-").reverse().join("-");
    // console.log(fromdate,todate,'pp')

    $.ajax({
        url: '/bleach_admin/ajax/sales-data3/',
        data: {
        // 'fromdate': fromdate,'todate':todate
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {

            var total_governorate_sales = 0;
            var gov_id = 1;
            var governorate_sales = [['Governorate', 'Sales']];

        $.each(data,function(key,value){
            console.log(value.governorate,parseInt(value.count),"gov")
            governorate_sales.push([value.governorate,value.count]);
            total_governorate_sales += parseInt(value.count)
        });

        // $('#clint2').text(total_sales);
        // console.log(data,"pop")
        console.log(total_governorate_sales,"tc")

        $.each(data,function(key,value){
           var percent = ((parseInt(value.count)*parseInt(100))/parseInt(total_governorate_sales));
           $('#c'+ gov_id++ +'').text(parseFloat(percent).toFixed(2));
        })

        var data = google.visualization.arrayToDataTable(governorate_sales);

        var options = {
            chartArea : {height: '80%',},
            width:300,
            title: "",
            pieHole: 0.4,
            animation: {
                duration:1000,
                easing:'out',
                startup: true
            },
            legend: 'none'
        };

        var chart = new google.visualization.PieChart(document.getElementById('donutchart3'));
        chart.draw(data, options);
        // initial value
        var percent = 0;
        // start the animation loop
        var handler = setInterval(function(){
            // values increment
            percent += 1;
            // apply new values
            data.setValue(0, 1, percent);
            data.setValue(1, 1, 100 - percent);
            // update the pie
            chart.draw(data, options);
            // check if we have reached the desired value
            if (percent > 74)
                // stop the loop
                clearInterval(handler);
        }, 30);

            }
    })
}

$("#cln_from").change(function(){
    console.log('room');
    drawChart3(); 
});

$("#cln_to").change(function(){
    console.log('room');
    drawChart3();   
});

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawsalescurvechart);

function drawsalescurvechart() {
if ($('#daym').val() == 'month') {
        var dom = 'Month' ;
        var from_my = $('#month1').val();
        var to_my = $('#month2').val();
        var fromdate= from_my;
        var todate= to_my;
        console.log(from_my, to_my, "monthd")
    }else{
        var dom = 'Date' ;
        var fromd = $('#from').val();
        var to = $('#to').val();

        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }


var dates = [];
var subs = [];
var apps = [];
$.ajax({
    url: '/bleach_admin/ajax/sales-curve-data/',
    data: {
    'fromdate': fromdate,'todate':todate, 'dom':dom
    },
    dataType: "json",
    type: "GET",
    contentType: "application/json;charset=utf-8",
    
    success: function(data) {
    console.log('lp')
    var sales = [['Date', 'Amount']];
    var sale_sum = 0;

    $.each(data,function(key,value){
        console.log(value.date,"uio")
        var vals = value.date.split('-');
        var year = parseInt(vals[0]);
        var month = parseInt (vals[1]);
        var day = parseInt (vals[2]);
        // console.log(year,month,day)
    sales.push([new Date(year,month-1,day),value.amount]);
        sale_sum += parseInt(value.amount);
    });

    $('#total_sales').text(sale_sum);

    var saleslist = google.visualization.arrayToDataTable(sales);

    var options = {
        chartArea : {height: '100%',},
        width:500,
        title: 'sales',
        curveType: 'function',
        legend: { position: 'bottom' },
        animation: {
        duration:1000,
        easing: 'out',
        startup:true
        },
        colors: ['blue'],
        lineWidth: 5,
    };

    var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

    chart.draw(saleslist, options);
    }
})
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

var date_a = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

var date_b = date1.getDate()-1  + "-" + date1.getMonth() + "-" + date1.getFullYear();

$('#from').val(date_b);
$('#to').val(date_a);

$('#monthpicker1').calendar({
    type: 'month'
});

$('#monthpicker2').calendar({
    type: 'month'
});

console.log($('#daym').val(),"run")
console.log($('#month1').val(),"mval")
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


$("#from").change(function(){
    console.log('room');
    drawsalescurvechart();   
});

$("#mnt_btn").on("click",function(){
    console.log($("#month1").val(),$("#month2").val(),'room');
    drawsalescurvechart();   
});

$("#to").change(function(){
    drawsalescurvechart();
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

    drawsalescurvechart();
})

$("#daym").change(function(){
        if ($(this).val() == 'month'){
            $('.set1').attr("hidden",true);
            $('.set2').attr("hidden",false);
            
            var date1 = new Date();
            var datestring = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            var date2 = new Date();
            date2.setDate(date2.getDate()-30);
            var datestring2 = date2.getDate()  + "/" + (date2.getMonth()+1) + "/" + date2.getFullYear();
            console.log(datestring,datestring2)

            $('#from').val(datestring2);
            $('#to').val(datestring);
            drawsalescurvechart();
        }
        else{
            $('.set1').attr("hidden",false);
            $('.set2').attr("hidden",true);
            var date1 = new Date();
            var datestring = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            var datestring2 = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            $('#from').val(datestring2);
            $('#to').val(datestring);
            drawsalescurvechart();

        }
    })