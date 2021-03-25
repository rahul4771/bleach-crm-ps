google.load('visualization', '1.0', {
    'packages': ['corechart']
});

// Set a callback to run when the Google Visualization API is loaded.
google.setOnLoadCallback(initialize);

function initialize() {
    console.log("drax2")
    var chart = new google.visualization.ChartWrapper({
        containerId: 'chart_div'
    });

    var data = [];

    var options = {
        chartArea : {height: '85%',},
        width: '100%',
        animation: {
            duration: 1000,
            easing: 'out'
        },
        
        series: {1: {lineWidth: 3, type: 'line',lineDashStyle: [5, 5], bold: true,}},
        colors: ['#ff8c56','#FFFF00'],
        legend:{position:'none'}
    };
    
    chart.setOptions(options);

    function drawArea() {
        // var date1 = new Date();

        var sales_month = $('#calendar_month').val();

        // var month = ("0" + (date1.getMonth()+1)).slice(-2);
        // console.log(month,"lp")
        
        // var datestring = month + "/" + date1.getFullYear();
        
        // console.log(datestring)      
        
        axios.get(url+'/api/daily-sales-chart/',{ params: { 'sales_month': sales_month } })
        .then(function (response) {
    
            $.each(response.data.list, function(key,value) {
            var quotations_area = [['Date', 'Total Cleaning Amount','Reference']];

            if(response.data.list.length > 0){
            $.each(response.data.list,function(key,value){

                var ord_date = new Date(value.date+"Z")

                quotations_area.push([ord_date,value.totalamount,2000]);
                
            });
            }else{
                quotations_area.push(['',0,2000]);
            }

            data[1] = new google.visualization.arrayToDataTable(quotations_area);

            chart.setChartType('LineChart');
            chart.setDataTable(data[1]);
            chart.draw();
            })
        })
        
    }

    drawArea();

    $("#calendar_month").on("change",(function(){
        drawArea();
    }));
    
}