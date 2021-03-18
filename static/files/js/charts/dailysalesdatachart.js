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

        function appendLeadingZeroes(n){
            if(n <= 9){
              return "0" + n;
            }
            return n
          }
        
        var date3 = new Date();
        
        date3.setDate(date3.getDate()-1)
        //date3.setMonth(date3.getMonth()+1)
        
        var datestring = appendLeadingZeroes(date3.getDate())  + "-" + appendLeadingZeroes(date3.getMonth()+1) + "-" + date3.getFullYear();
        
        var date4 = new Date();
        date4.setDate(date4.getDate()-30);
        //date4.setMonth(date4.getMonth()+1);
        var datestring2 = appendLeadingZeroes(date4.getDate())  + "-" + appendLeadingZeroes(date4.getMonth()+1) + "-" + date4.getFullYear();
        
        console.log(datestring,datestring2)

        
        
        axios.get(url+'/api/daily-sales-chart/',{ params: { 'start_date': datestring,'end_date':datestring2 } })
        .then(function (response) {
            console.log(response.data,"war")
    
            $.each(response.data.list, function(key,value) {
            var quotations_area = [['Date', 'General Cleaning', 'Upholstery Cleaning', 'Kitchen Cleaning', 'Deep Cleaning', 'Carpet Cleaning', 'Sterilization']];

            if(response.data.list.length > 0){
            $.each(response.data.list,function(key,value){
                console.log(response.data.list,"dtss")
                var vals = value.date.split('-');
                console.log(vals,vals[2],vals[1],vals[0],"datev")
                var year = parseInt(vals[0]);
                var month = parseInt (vals[1]);
                var day = parseInt (vals[2]);
                console.log(year,month,day,"ter")

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
    
}