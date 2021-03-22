console.log("drax1")
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

    function drawArea() {
        console.log("drax3")
        var date1 = new Date();

        var month = ("0" + (date1.getMonth()+1)).slice(-2);
        console.log(month,"lp")
        
        var datestring = month + "/" + date1.getFullYear();
        
        console.log(datestring)      
        
        axios.get(url+'/api/daily-sales-chart/',{ params: { 'sales_month': datestring } })
        .then(function (response) {
            console.log(response.data,"war444")
    
            $.each(response.data.list, function(key,value) {
            var quotations_area = [['Date', 'General Cleaning', 'Upholstery Cleaning', 'Kitchen Cleaning', 'Deep Cleaning', 'Carpet Cleaning', 'Sterilization']];

            if(response.data.list.length > 0){
            $.each(response.data.list,function(key,value){

                var ord_date = new Date(value.date+"Z")
                console.log(ord_date,"ord")
                // ord_date.setMonth(ord_date.getMonth()-1);
                // console.log(ord_date,"ord2")

                console.log(quotations_area,"qts_test")

                quotations_area.push([ord_date,value.GeneralCleaning,value.UpholsteryCleaning,value.KitchenCleaning,value.DeepCleaning,value.CarpetCleaning,value.Sterilization]);
                console.log(quotations_area,"qts_test2")
                
            });
            }else{
                quotations_area.push(['',0,0,0,0,0,0]);
            }
            
            console.log(quotations_area,"qts")

            data[1] = new google.visualization.arrayToDataTable(quotations_area);

            chart.setChartType('LineChart');
            chart.setDataTable(data[1]);
            chart.draw();
            })
        })
        
    }

    drawArea();
    
}