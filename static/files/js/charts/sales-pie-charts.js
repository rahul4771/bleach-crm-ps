var colors = ['#3366cc', '#dc3912', '#ff9900', '#109618', '#990099', '#0099c6'];

function toTitleCase(str)
{
    return str.replace(/\w+/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

//donut chart
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawlocationChart);
function drawlocationChart() {

    if ($('#daymonth_location').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#location_pie_date1').val();
        var to = $('#location_pie_date2').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{

        var dom = 'Month' ;
        var fromdate= $('#location_pie_month1').val();
        var todate= $('#location_pie_month2').val();
        console.log(fromdate, todate, "monthd22")
    }

    $.ajax({
        url: '/bleach_admin/ajax/sales-data/',
        data: {
        'fromdate': fromdate,'todate':todate, 'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data_location) {
            console.log(data_location,"dataloc")
            if (data_location.length == 0){
                $('#donutchart1').attr("hidden",true);
                $('#locationnodata').attr("hidden",false);
                $("#legend_location").empty();
            }else{
                $('#locationnodata').attr("hidden",true);
                $('#donutchart1').attr("hidden",false);

                var total_sales = 0;
                var cid = 1;
                var location_sales = [['Location', 'Sales']];
            
                $.each(data_location,function(key,value){
                    console.log(value.location,parseInt(value.count),"govlo")
                    var location = toTitleCase(value.location)
                    location_sales.push([location,value.count]);
                    total_sales += parseInt(value.count)
                });

                var data = google.visualization.arrayToDataTable(location_sales);

                var options = {
                    chartArea : {height: '80%',left:'0%',right:'50%'},
                    width:'100%',
                    title: "",
                    pieHole: 0.4,
                    animation: {
                        duration:1000,
                        easing:'out',
                        startup: true
                    },
                    legend: {position:'none'}
                };

                var chart = new google.visualization.PieChart(document.getElementById('donutchart1'));
                chart.draw(data, options);

                var total = 0;
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    total += data.getValue(i, 1);
                }
                
                $("#legend_location").empty();
                var legend = document.getElementById("legend_location");
                var legItem = [];
                
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    if (i < 5){
                    var label = data.getValue(i, 0);
                    var value = data.getValue(i, 1);
                    var percent = Number(100 * value / total).toFixed(1);
                    if (isNaN(percent)) percent = 0.0; 
                    console.log(percent,"percdf")
                    // This will create legend list for the display
                    if (percent > 0){
                    legItem[i] = document.createElement('div');
                    legItem[i].className = 'donut-char-legend';
                    legItem[i].id = 'legend_' + data.getValue(i, 0);
                    
                    legItem[i].innerHTML = '<i class="fa fa-square" style="color:'+colors[i]+'"></i> <div class="chart-stat">' + label + '</div><span>' + percent + ' %</span>';

                    legend.appendChild(legItem[i]);
                    }
                }
                }

                var others = 0;

                for (var j = 5; j < data_location.length; j++){
                    console.log(j,"joy")
                    others += data.getValue(j, 1);
                    
                }

                if (others != 0){
                    console.log(others,"ott")
                    var others_percent = Number(100 * others / total).toFixed(1);
                    if (isNaN(others_percent)) others_percent = 0.0;
                    console.log(others,others_percent,"otp")
                    $('#legend_location').append('<div class="donut-char-legend" ><i class="fa fa-square" style="color:#0099c6"></i> <div class="chart-stat">Others</div><span>' + others_percent + ' %</span></div>')
                }
                $('#location_loader').attr("hidden",true);

            }

            
            }

    })
}

$("#location_pie_data").click(function(){
    console.log('room');
    var d1 = $('#location_pie_date1').val();
    var d2 = $('#location_pie_date2').val();
    if ( d1 > d2){
        $('#location_pie_date1').val(d2);
        $('#location_pie_date2').val(d1);
    }
    drawlocationChart(); 
});

$("#daymonth_location").click(function(){
    if ($(this).is(':checked')){

        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        
        drawlocationChart();

    }
    else{
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);

        drawlocationChart();

    }
})

$("#reset_locations").click(function(){
    var date1 = new Date();
    date1.setDate(date1.getDate()-1)
    
    var datestring = appendLeadingZeroes(date1.getDate())  + "-" + appendLeadingZeroes(date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
   
    var datestring2 = appendLeadingZeroes(date2.getDate())  + "-" + appendLeadingZeroes(date2.getMonth()+1) + "-" + date2.getFullYear();

    $('#location_pie_date1').val(datestring2);
    $('#location_pie_date2').val(datestring);

    var date3 = new Date();
    date3.setMonth(date3.getMonth()-1);

    var date4 = new Date();

    var month = appendLeadingZeroes(date3.getMonth()+1);
    var month2 = appendLeadingZeroes(date4.getMonth()+1);

    var monthstring = month + "/" + date3.getFullYear();
    var monthstring2 = month2 + "/" + date4.getFullYear();

    $('#location_pie_month1').val(monthstring);
    $('#location_pie_month2').val(monthstring2);
    drawlocationChart();
})

//donut chart2
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawcleaningtypeChart);
function drawcleaningtypeChart() {
    if ($('#daymonth_cleaningtype').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#cleaningtype_pie_date1').val();
        var to = $('#cleaningtype_pie_date2').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{

        var dom = 'Month' ;
        var fromdate= $('#cleaningtype_pie_month1').val();
        var todate= $('#cleaningtype_pie_month2').val();
        console.log(fromdate, todate, "monthd224")
    }

    $.ajax({
        url: '/bleach_admin/ajax/sales-data2/',
        data: {
        'fromdate': fromdate,'todate':todate, 'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data_cleaning) {

        if (data_cleaning.length == 0){
            $('#donutchart2').attr("hidden",true);
            $('#cleaningnodata').attr("hidden",false);
            $("#legend_cleaning").empty();
            $('#cleaning_loader').attr("hidden",true);
        }else{
            $('#donutchart2').attr("hidden",false);
            $('#cleaningnodata').attr("hidden",true);

            var total_cleaningtype_sales = 0;
            var clean_id = 1;
            var cleaningtype_sales = [['Cleaning Type', 'Sales']];
        
        $.each(data_cleaning,function(key,value){
            console.log(value.cleaning_type,parseInt(value.count),"gov")
            cleaningtype_sales.push([value.cleaning_type,value.count]);
            total_cleaningtype_sales += parseInt(value.count)
        });

        // $('#clint2').text(total_sales);
        // console.log(data,"pop")

        var data = google.visualization.arrayToDataTable(cleaningtype_sales);

        var options = {
            chartArea : {height: '80%',left:'0%',right:'50%'},
            width:'100%',
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

        var total = 0;
        for (var i = 0; i < data.getNumberOfRows(); i++) {
            total += data.getValue(i, 1);
        }
        
        $("#legend_cleaning").empty();
        var legend = document.getElementById("legend_cleaning");
        var legItem = [];
        
        for (var i = 0; i < data.getNumberOfRows(); i++) {
            var label = data.getValue(i, 0);
            var split_label = label.split(" ")
            var value = data.getValue(i, 1);
            var percent = Number(100 * value / total).toFixed(1);
            if (isNaN(percent)) percent = 0.0; 
            console.log(percent,"perc")
            // This will create legend list for the display
            legItem[i] = document.createElement('div');
            legItem[i].className = 'donut-char-legend';
            legItem[i].id = 'legend_' + data.getValue(i, 0);
            legItem[i].innerHTML = '<i class="fa fa-square" style="color:'+colors[i]+'"></i> <div class="chart-stat">' + split_label[0] + '</div><span>' + percent + ' %</span>';

            legend.appendChild(legItem[i]);
        }
        $('#cleaning_loader').attr("hidden",true);
        
            }
        }
    })
}

$("#cleaningtype_pie_data").click(function(){
    console.log('room');
    var d1 = $('#cleaningtype_pie_date1').val();
    var d2 = $('#cleaningtype_pie_date2').val();
    if ( d1 > d2){
        $('#cleaningtype_pie_date1').val(d2);
        $('#cleaningtype_pie_date2').val(d1);
    }
    drawcleaningtypeChart(); 
});

$("#daymonth_cleaningtype").click(function(){
    if ($(this).is(':checked')){

        $('.clnset1').attr("hidden",false);
        $('.clnset2').attr("hidden",true);
        
        drawcleaningtypeChart();

    }
    else{
        $('.clnset1').attr("hidden",true);
        $('.clnset2').attr("hidden",false);

        drawcleaningtypeChart();

    }
})

$("#reset_cleaningtypes").click(function(){
    var date1 = new Date();

    date1.setDate(date1.getDate()-1)
    
    var datestring = appendLeadingZeroes(date1.getDate())  + "-" + appendLeadingZeroes(date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    
    var datestring2 = appendLeadingZeroes(date2.getDate())  + "-" + appendLeadingZeroes(date2.getMonth()+1) + "-" + date2.getFullYear();

    $('#cleaningtype_pie_date1').val(datestring2);
    $('#cleaningtype_pie_date2').val(datestring);

    var date3 = new Date();
    date3.setMonth(date3.getMonth()-1);

    var date4 = new Date();

    var month = appendLeadingZeroes(date3.getMonth()+1);
    var month2 = appendLeadingZeroes(date4.getMonth()+1);

    var monthstring = month + "/" + date3.getFullYear();
    var monthstring2 = month2 + "/" + date4.getFullYear();

    $('#cleaningtype_pie_month1').val(monthstring);
    $('#cleaningtype_pie_month2').val(monthstring2);
    drawcleaningtypeChart();
})

//donut chart3
google.charts.load("current", {packages:["corechart"]});
google.charts.setOnLoadCallback(drawgovernorateChart);
function drawgovernorateChart() {
    if ($('#daymonth_governorate').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#governorate_pie_date1').val();
        var to = $('#governorate_pie_date2').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{

        var dom = 'Month' ;
        var fromdate= $('#governorate_pie_month1').val();
        var todate= $('#governorate_pie_month2').val();
        console.log(fromdate, todate, "monthd")
    }

    $.ajax({
        url: '/bleach_admin/ajax/sales-data3/',
        data: {
        'fromdate': fromdate,'todate':todate, 'dom':dom
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data_governorate) {

        if (data_governorate.length == 0){
            $('#donutchart3').attr("hidden",true);
            $('#governoratenodata').attr("hidden",false);
            $("#legend_governorate").empty();
            $('#governorate_loader').attr("hidden",true);
        }else{
            $('#donutchart3').attr("hidden",false);
            $('#governoratenodata').attr("hidden",true);
            
            var total_governorate_sales = 0;
            var gov_id = 1;
            var governorate_sales = [['Governorate', 'Sales']];

        $.each(data_governorate,function(key,value){
            console.log(value.governorate,parseInt(value.count),"gov")
            governorate_sales.push([value.governorate,value.count]);
            total_governorate_sales += parseInt(value.count)
        });

        var data = google.visualization.arrayToDataTable(governorate_sales);

        var options = {
            chartArea : {height: '80%',left:'0%',right:'50%'},
            width:'100%',
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

        var total = 0;
        for (var i = 0; i < data.getNumberOfRows(); i++) {
            total += data.getValue(i, 1);
        }
        
        $("#legend_governorate").empty();
        var legend = document.getElementById("legend_governorate");
        var legItem = [];
        
        for (var i = 0; i < data.getNumberOfRows(); i++) {
            var label = data.getValue(i, 0);
            if (label == 'Mubarak Al-Kabeer'){
                label = 'Mub. Al-Kabeer'
            }
            var value = data.getValue(i, 1);
            var percent = Number(100 * value / total).toFixed(1);
            if (isNaN(percent)) percent = 0.0; 
            console.log(percent,"perc")
            // This will create legend list for the display
            legItem[i] = document.createElement('div');
            legItem[i].className = 'donut-char-legend';
            legItem[i].id = 'legend_' + data.getValue(i, 0);
            legItem[i].innerHTML = '<i class="fa fa-square" style="color:'+colors[i]+'"></i> <div class="chart-stat">' + label + '</div><span>' + percent + ' %</span>';

            legend.appendChild(legItem[i]);
        }
        $('#governorate_loader').attr("hidden",true);
            }
        }
    })
}

$("#governorate_pie_data").click(function(){
    console.log('room');
    var d1 = $('#governorate_pie_date1').val();
    var d2 = $('#governorate_pie_date2').val();
    if ( d1 > d2){
        $('#governorate_pie_date1').val(d2);
        $('#governorate_pie_date2').val(d1);
    }
    drawgovernorateChart(); 
});

$("#daymonth_governorate").click(function(){
    if ($(this).is(':checked')){

        $('.govset1').attr("hidden",false);
        $('.govset2').attr("hidden",true);
        
        drawgovernorateChart();

    }
    else{
        $('.govset1').attr("hidden",true);
        $('.govset2').attr("hidden",false);

        drawgovernorateChart();

    }
})

$("#reset_governorates").click(function(){
    var date1 = new Date();
    date1.setDate(date1.getDate()-1)
    
    var datestring = appendLeadingZeroes(date1.getDate())  + "-" + appendLeadingZeroes(date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
   
    var datestring2 = appendLeadingZeroes(date2.getDate())  + "-" + appendLeadingZeroes(date2.getMonth()+1) + "-" + date2.getFullYear();

    $('#governorate_pie_date1').val(datestring2);
    $('#governorate_pie_date2').val(datestring);

    var date3 = new Date();
    date3.setMonth(date3.getMonth()-1);

    var date4 = new Date();

    var month = appendLeadingZeroes(date3.getMonth()+1);
    var month2 = appendLeadingZeroes(date4.getMonth()+1);

    var monthstring = month + "/" + date3.getFullYear();
    var monthstring2 = month2 + "/" + date4.getFullYear();
    console.log(monthstring,monthstring2,"dts")

    $('#governorate_pie_month1').val(monthstring);
    $('#governorate_pie_month2').val(monthstring2);
    drawgovernorateChart();
})

// 0 append to single digit date and month
function appendLeadingZeroes(n){
    if(n <= 9){
      return "0" + n;
    }
    return n
  }

// month picker month add
var date1 = new Date();
date1.setMonth(date1.getMonth()-1);

var date2 = new Date();

var month = appendLeadingZeroes(date1.getMonth()+1);
var month2 = appendLeadingZeroes(date2.getMonth()+1);

var monthstring = month + "/" + date1.getFullYear();
var monthstring2 = month2 + "/" + date2.getFullYear();

$('#location_pie_month1').val(monthstring);
$('#location_pie_month2').val(monthstring2);

$('#cleaningtype_pie_month1').val(monthstring);
$('#cleaningtype_pie_month2').val(monthstring2);

$('#governorate_pie_month1').val(monthstring);
$('#governorate_pie_month2').val(monthstring2);

//datepicker dates
var date3 = new Date();

date3.setDate(date3.getDate()-1)

var datestring = appendLeadingZeroes(date3.getDate())  + "-" + appendLeadingZeroes(date3.getMonth()+1) + "-" + date3.getFullYear();

var date4 = new Date();
date4.setDate(date4.getDate()-30);

var datestring2 = appendLeadingZeroes(date4.getDate())  + "-" + appendLeadingZeroes(date4.getMonth()+1) + "-" + date2.getFullYear();

$('#cleaningtype_pie_date1').val(datestring2);
$('#cleaningtype_pie_date2').val(datestring);

$('#location_pie_date1').val(datestring2);
$('#location_pie_date2').val(datestring);

$('#governorate_pie_date1').val(datestring2);
$('#governorate_pie_date2').val(datestring);


if ($('#daymonth_location').is(':checked')) {
    console.log("runnon")
    $('.set1').attr("hidden",false);
    $('.set2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.set1').attr("hidden",true);
    $('.set2').attr("hidden",false);
}

if ($('#daymonth_cleaningtype').is(':checked')) {
    console.log("runnon")
    $('.clnset1').attr("hidden",false);
    $('.clnset2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.clnset1').attr("hidden",true);
    $('.clnset2').attr("hidden",false);
}

if ($('#daymonth_governorate').is(':checked')) {
    console.log("runnon")
    $('.govset1').attr("hidden",false);
    $('.govset2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.govset1').attr("hidden",true);
    $('.govset2').attr("hidden",false);
}


