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