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
        
        success: function(data) {

            var total_sales = 0;
            var cid = 1;
            var location_sales = [['Location', 'Sales']];

        $.each(data,function(key,value){
            console.log(value.location,parseInt(value.count),"gov")
            location_sales.push([value.location,value.count]);
            total_sales += parseInt(value.count)
        });

        $.each(data,function(key,value){
            var percent = ((parseInt(value.count)*parseInt(100))/parseInt(total_sales)) ;
           
            if (total_sales == 0){
                console.log("red")
                $('#loc'+ cid++ +'').text('0.0');
            }else{
                console.log("blue")
                $('#loc'+ cid++ +'').text(parseFloat(percent).toFixed(1));
            }
        })

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
            legend: 'none'
        };

        var chart = new google.visualization.PieChart(document.getElementById('donutchart1'));
        chart.draw(data, options);
        // // initial value
        // var percent = 0;
        // // start the animation loop
        // var handler = setInterval(function(){
        //     // values increment
        //     percent += 1;
        //     // apply new values
        //     data.setValue(0, 1, percent);
        //     data.setValue(1, 1, 100 - percent);
        //     // update the pie
        //     chart.draw(data, options);
        //     // check if we have reached the desired value
        //     if (percent > 74)
        //         // stop the loop
        //         clearInterval(handler);
        // }, 30);
            $('.donut1').attr("hidden",false);
            }
    })
}

$("#location_pie_data").click(function(){
    console.log('room');
    drawlocationChart(); 
});

$("#daymonth_location").click(function(){
    if ($(this).is(':checked')){

        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#location_pie_date1').val(datestring2);
        $('#location_pie_date2').val(datestring);
        drawlocationChart();

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

        $('#location_pie_month1').val(datestring);
        $('#location_pie_month2').val(datestring2);

        drawlocationChart();

    }
})

$("#reset_locations").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#location_pie_date1').val(datestring2);
    $('#location_pie_date2').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var monthstring = month + "/" + date1.getFullYear();
    var monthstring2 = month2 + "/" + date1.getFullYear();
    console.log(monthstring,monthstring2,"dts")

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
        console.log(total_cleaningtype_sales,"totcle")

        $.each(data,function(key,value){
           var percentage = ((parseInt(value.count)*parseInt(100))/(parseInt(total_cleaningtype_sales)));
           if (total_cleaningtype_sales == 0){
            $('#c'+ clean_id++ +'').text('0.0');
           }else{
            $('#c'+ clean_id++ +'').text(parseFloat(percentage).toFixed(1));
           }
        })

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
        // // initial value
        // var percent = 0;
        // //start the animation loop
        // var handler = setInterval(function(){
        //     // values increment
        //     percent += 1;
        //     // apply new values
        //     data.setValue(0, 1, percent);
        //     data.setValue(1, 1, 100 - percent);
        //     // update the pie
        //     chart.draw(data, options);
        //     // check if we have reached the desired value
        //     if (percent > 74)
        //         // stop the loop
        //         clearInterval(handler);
        // }, 30);
        $('.donut2').attr("hidden",false);
            }
    })
}

$("#cleaningtype_pie_data").click(function(){
    console.log('room');
    drawcleaningtypeChart(); 
});

$("#daymonth_cleaningtype").click(function(){
    if ($(this).is(':checked')){

        $('.clnset1').attr("hidden",false);
        $('.clnset2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#cleaningtype_pie_date1').val(datestring2);
        $('#cleaningtype_pie_date2').val(datestring);
        drawcleaningtypeChart();

    }
    else{
        $('.clnset1').attr("hidden",true);
        $('.clnset2').attr("hidden",false);
        
        var date1 = new Date();
        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();

        $('#cleaningtype_pie_month1').val(datestring);
        $('#cleaningtype_pie_month2').val(datestring2);

        drawcleaningtypeChart();

    }
})

$("#reset_cleaningtypes").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#cleaningtype_pie_date1').val(datestring2);
    $('#cleaningtype_pie_date2').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var monthstring = month + "/" + date1.getFullYear();
    var monthstring2 = month2 + "/" + date1.getFullYear();
    console.log(monthstring,monthstring2,"dts")

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
           if (total_governorate_sales == 0){
            $('#gov'+ gov_id++ +'').text('0.0');
           }else{
            $('#gov'+ gov_id++ +'').text(parseFloat(percent).toFixed(1));
           }
        })

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
        // // initial value
        // var percent = 0;
        // // start the animation loop
        // var handler = setInterval(function(){
        //     // values increment
        //     percent += 1;
        //     // apply new values
        //     data.setValue(0, 1, percent);
        //     data.setValue(1, 1, 100 - percent);
        //     // update the pie
        //     chart.draw(data, options);
        //     // check if we have reached the desired value
        //     if (percent > 74)
        //         // stop the loop
        //         clearInterval(handler);
        // }, 30);
        $('.donut3').attr("hidden",false);
            }
    })
}

$("#governorate_pie_data").click(function(){
    console.log('room');
    drawgovernorateChart(); 
});

$("#daymonth_governorate").click(function(){
    if ($(this).is(':checked')){

        $('.govset1').attr("hidden",false);
        $('.govset2').attr("hidden",true);
        var date1 = new Date();
        var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#governorate_pie_date1').val(datestring2);
        $('#governorate_pie_date2').val(datestring);
        drawcgovernorateChart();

    }
    else{
        $('.govset1').attr("hidden",true);
        $('.govset2').attr("hidden",false);
        
        var date1 = new Date();
        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();

        $('#governorate_pie_month1').val(datestring);
        $('#governorate_pie_month2').val(datestring2);

        drawgovernorateChart();

    }
})

$("#reset_governorates").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#governorate_pie_date1').val(datestring2);
    $('#governorate_pie_date2').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var monthstring = month + "/" + date1.getFullYear();
    var monthstring2 = month2 + "/" + date1.getFullYear();
    console.log(monthstring,monthstring2,"dts")

    $('#governorate_pie_month1').val(monthstring);
    $('#governorate_pie_month2').val(monthstring2);
    drawgovernorateChart();
})

//sales curve chart
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawsalescurveChart);

function drawsalescurveChart() {
    if ($('#daymonth_sales').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#sales_curve_date1').val();
        var to = $('#sales_curve_date2').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{

        var dom = 'Month' ;
        var fromdate= $('#sales_curve_month1').val();
        var todate= $('#sales_curve_month2').val();
        console.log(fromdate, todate, "monthd")
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
    var total_sum = 0;
    
    if(data.length > 0){
        $.each(data,function(key,value){
            console.log(value.date,"uio")
            var vals = value.date.split('-');
            var year = parseInt(vals[0]);
            var month = parseInt (vals[1]);
            var day = parseInt (vals[2]);
            // console.log(year,month,day)
        sales.push([new Date(year,month-1,day),value.amount]);
            sale_sum += parseInt(value.amount);
            total_sum += parseInt(value.total);
        });
    }else{
        var vals = $('#sales_curve_month1').val().split('/');
        var year = parseInt(vals[1]);
        var month = parseInt (vals[0]);
        var day = parseInt (01);
        console.log(year,month,day,"testg");
        sales.push([new Date(year,month-1,day),0]);
        sale_sum = 0;
        total_sum = 0;
    }
    console.log(sales,"sls")
    $('#total_sales').text(sale_sum);
    $('#total_orders').text(total_sum);

    var saleslist = google.visualization.arrayToDataTable(sales);

    var options = {
        chartArea : {height: '80%',},
        width:'100%',
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

$("#daymonth_sales").click(function(){
    if ($(this).is(':checked')){

        $('.saleset1').attr("hidden",false);
        $('.saleset2').attr("hidden",true);
        var date1 = new Date();
        var datestring = (date1.getDate()-1)  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = (date1.getDate()-1)  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#sales_curve_date1').val(datestring2);
        $('#sales_curve_date2').val(datestring);
        drawsalescurveChart();

    }
    else{
        $('.saleset1').attr("hidden",true);
        $('.saleset2').attr("hidden",false);
        
        var date1 = new Date();
        var month = ("0" + (date1.getMonth()-1)).slice(-2);
        var month2 = ("0" + (date1.getMonth())).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();
        console.log(datestring,datestring2,"dts")
        $('#sales_curve_month1').val(datestring);
        $('#sales_curve_month2').val(datestring2);

        drawsalescurveChart();

    }
})

$('#sales_curve_month1').change(function(){
    drawsalescurveChart();
});

$('#sales_curve_month2').change(function(){
    drawsalescurveChart();
});

$('#sales_curve_date1').change(function(){
    drawsalescurveChart();
});

$('#sales_curve_date2').change(function(){
    drawsalescurveChart();
})

$("#reset_sales_curve").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#sales_curve_date1').val(datestring2);
    $('#sales_curve_date2').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var monthstring = month + "/" + date1.getFullYear();
    var monthstring2 = month2 + "/" + date1.getFullYear();
    console.log(monthstring,monthstring2,"dts")

    $('#sales_curve_month1').val(monthstring);
    $('#sales_curve_month2').val(monthstring2);
    drawsalescurveChart();
})

$("#daym").change(function(){
        if ($(this).val() == 'month'){
            $('.saleset1').attr("hidden",true);
            $('.saleset2').attr("hidden",false);
            
            var date1 = new Date();
            var datestring = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            var date2 = new Date();
            date2.setDate(date2.getDate()-30);
            var datestring2 = date2.getDate()  + "/" + (date2.getMonth()+1) + "/" + date2.getFullYear();
            console.log(datestring,datestring2)

            $('#from').val(datestring2);
            $('#to').val(datestring);
            drawsalescurveChart();
        }
        else{
            $('.saleset1').attr("hidden",false);
            $('.saleset2').attr("hidden",true);
            var date1 = new Date();
            var datestring = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            var datestring2 = date1.getDate()  + "/" + (date1.getMonth()+1) + "/" + date1.getFullYear();

            $('#from').val(datestring2);
            $('#to').val(datestring);
            drawsalescurveChart();

        }
    })

function salestarget(evaluator_id){
console.log(evaluator_id,"evid")

//sales target chart
google.charts.load('current',{
callback: function () {
    drawsalestargetChart();
    $(window).resize(drawsalestargetChart);
},
'packages':['corechart']});
google.charts.setOnLoadCallback(drawsalestargetChart);

//googlechart
function drawsalestargetChart() {
    
    if ($('#daymonth_sales_target').is(':checked')) {
        var dom = 'Date' ;
        var fromd = $('#sales_target_date1').val();
        var to = $('#sales_target_date2').val();
    
        var fromdate= fromd.split("-").reverse().join("-");
        var todate= to.split("-").reverse().join("-");
        console.log(fromdate,todate,'pp')
    }else{

        var dom = 'Month' ;
        var fromdate= $('#sales_target_month1').val();
        var todate= $('#sales_target_month2').val();
        console.log(fromdate, todate, "monthd")
    }
    

    $.ajax({
        url: '/bleach_admin/ajax/sales-target-data/',
        data: {
        'fromdate': fromdate,'todate':todate, 'dom':dom, 'evaluator':evaluator_id
        },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
        console.log('lp')
        var sales = [['Date', 'Amount']];
        var sale_sum = 0;
        var total_sum = 0;
        
        if(data.length > 0){
            $.each(data,function(key,value){
                console.log(value.date,"uio")
                var vals = value.date.split('-');
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                // console.log(year,month,day)
            sales.push([new Date(year,month-1,day),value.amount]);
                sale_sum += parseInt(value.amount);
                total_sum += parseInt(value.total);
            });
        }else{
            var vals = $('#sales_target_month1').val().split('/');
            var year = parseInt(vals[1]);
            var month = parseInt (vals[0]);
            var day = parseInt (01);
            console.log(year,month,day,"testg");
            sales.push([new Date(year,month-1,day),0]);
            sale_sum = 0;
            total_sum = 0;
        }
        console.log(sales,"sls")
        $('#total_sales2').text(sale_sum);
        $('#total_orders2').text(total_sum);

    var quotations = google.visualization.arrayToDataTable(sales);

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
    })
}

$("#daymonth_sales_target").click(function(){
    console.log("dark")
    if ($(this).is(':checked')){

        $('.targetset1').attr("hidden",false);
        $('.targetset2').attr("hidden",true);
        var date1 = new Date();
        var datestring = (date1.getDate()-1)  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        var datestring2 = (date1.getDate()-1)  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

        $('#sales_target_date1').val(datestring2);
        $('#sales_target_date2').val(datestring);
        drawsalestargetChart();

    }
    else{
        $('.targetset1').attr("hidden",true);
        $('.targetset2').attr("hidden",false);
        
        var date1 = new Date();
        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
        console.log(month,"lp")
        var datestring = month + "/" + date1.getFullYear();
        var datestring2 = month2 + "/" + date1.getFullYear();
        console.log(datestring,datestring2,"dts")
        $('#sales_target_month1').val(datestring);
        $('#sales_target_month2').val(datestring2);

        drawsalestargetChart();

    }
})

$('#sales_target_month1').change(function(){
    drawsalestargetChart();
});

$('#sales_target_month2').change(function(){
    drawsalestargetChart();
});

$('#sales_target_date1').change(function(){
    drawsalestargetChart();
});

$('#sales_target_date2').change(function(){
    drawsalestargetChart();
})

$("#reset_sales_target").click(function(){
    var date1 = new Date();
    var datestring = date1.getDate()  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-30);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#sales_target_date1').val(datestring2);
    $('#sales_target_date2').val(datestring);

    var month = ("0" + (date1.getMonth())).slice(-2);
    var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")
    var monthstring = month + "/" + date1.getFullYear();
    var monthstring2 = month2 + "/" + date1.getFullYear();
    console.log(monthstring,monthstring2,"dts")

    $('#sales_target_month1').val(monthstring);
    $('#sales_target_month2').val(monthstring2);
    drawsalestargetChart();
})

}




var date1 = new Date();
var month = ("0" + (date1.getMonth())).slice(-2);
var month2 = ("0" + (date1.getMonth()+1)).slice(-2);
console.log(month,"lp")
var datestring = month + "/" + date1.getFullYear();
var datestring2 = month2 + "/" + date1.getFullYear();

$('#location_pie_month1').val(datestring);
$('#location_pie_month2').val(datestring2);

$('#cleaningtype_pie_month1').val(datestring);
$('#cleaningtype_pie_month2').val(datestring2);

$('#governorate_pie_month1').val(datestring);
$('#governorate_pie_month2').val(datestring2);

$('#sales_curve_month1').val(datestring);
$('#sales_curve_month2').val(datestring2);

$('#sales_target_month1').val(datestring);
$('#sales_target_month2').val(datestring2);

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

if ($('#daymonth_sales').is(':checked')) {
    console.log("runnon")
    $('.saleset1').attr("hidden",false);
    $('.saleset2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.saleset1').attr("hidden",true);
    $('.saleset2').attr("hidden",false);
}

if ($('#daymonth_sales_target').is(':checked')) {
    console.log("runnon")
    $('.targetset1').attr("hidden",false);
    $('.targetset2').attr("hidden",true);
}
else{
    console.log("runn")
    $('.targetset1').attr("hidden",true);
    $('.targetset2').attr("hidden",false);
}


