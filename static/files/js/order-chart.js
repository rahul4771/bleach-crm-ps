google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// function drawChart() {
//     var data = google.visualization.arrayToDataTable([
//       ['Year', 'Sales', 'Expenses'],
//       ['2013',  1000,      400],
//       ['2014',  1170,      460],
//       ['2015',  660,       1120],
//       ['2016',  1030,      540]
//     ]);

//     var options = {
//       title: 'Company Performance',
//       hAxis: {title: 'Year',  titleTextStyle: {color: '#333'}},
//       vAxis: {minValue: 0}
//     };

//     var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
//     chart.draw(data, options);
//   }
//googlechart
function drawChart() {
    
    // var fromd = $('#from').val();
    // var to = $('#to').val();

    // var fromdate= fromd.split("-").reverse().join("-");
    // var todate= to.split("-").reverse().join("-");
    // console.log(fromdate,todate,'pp')
    
    var dates = [];
    var subs = [];
    var apps = [];

    $.ajax({
        url: '/order-data/quotation_data',
        // data: {
        // 'fromdate': fromdate,'todate':todate
        // },
        dataType: "json",
        type: "GET",
        contentType: "application/json;charset=utf-8",
        
        success: function(data) {
        console.log('lp')
        var quotes = [['Date', 'Submitted', 'Approved']];
        var sub_sum = 0;
        var app_sum = 0;

        $.each(data,function(key,value){
            console.log(value.date,"uio")
            var vals = value.date.split('-');
            var year = parseInt(vals[0]);
            var month = parseInt (vals[1]);
            var day = parseInt (vals[2]);
            // console.log(year,month,day)
        quotes.push([new Date(year,month-1,day),value.sub_qt,value.app_qt]);
            sub_sum += parseInt(value.sub_qt);
            app_sum += parseInt(value.app_qt);
            dates.push(new Date(value.date));
            subs.push(value.sub_qt);
            apps.push(value.app_qt);
        });
        
        //console.log(quotes,"war ");
        $('#total_subs').text(sub_sum);
        $('#total_apps').text(app_sum);

        var quotations = google.visualization.arrayToDataTable(quotes);

        var options = {
            animation: {
            duration: 2000,
            easing: 'linear',
            startup:true
            },
            title: 'Quotations',
            hAxis: {title: 'Year',  titleTextStyle: {color: '#333'}},
            vAxis: {minValue: 0}
        };

        var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
        chart.draw(quotations, options);
        }
    });
}