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
        hAxis: {
            viewWindow:{ min: 0 },
            minValue: 0,
            format: '#'
        },
        vAxis: { textPosition: 'none' },
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
            url: "/agent/ajax/clientdata/",
            data: {
            'fromdate': month_1,'todate':month_2,'dom':dom2
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_month) {
            var clients = [['Governorate', 'Clients',{ role: 'style' },{ role: 'annotation' }]];
            var total_clients = 0;
            //var count = 0;

            $.each(data_month,function(key,value){
                
                color = '#ffc056';

                clients.push([value.governorate,value.clients,color,value.governorate]);
                total_clients += parseInt(value.clients)
                
            });

            console.log(total_clients,"war2 ");
            $('#totalclients').text(total_clients);


            data[0] = new google.visualization.arrayToDataTable(clients);

            chart.setChartType('BarChart');
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
            url: "/agent/ajax/clientdata/",
            data: {
            'fromdate': fromdate,'todate':todate,'dom':dom
            },
            dataType: "json",
            type: "GET",
            contentType: "application/json;charset=utf-8",
            
            success: function(data_date) {
            var clients = [['Governorate', 'Clients',{ role: 'style' },{ role: 'annotation' }]];
            var total_clients = 0;

            $.each(data_date,function(key,value){              

                clients.push([value.governorate,value.clients,'#ffc056',value.governorate]);
                total_clients += parseInt(value.clients)
                
            });

            console.log(total_clients,"war2 ");
            $('#totalclients').text(total_clients);

            data[1] = new google.visualization.arrayToDataTable(clients);

            chart.setChartType('BarChart');
            chart.setDataTable(data[1]);
            chart.draw();
        }
        });
    }
    
    $("#daymonthtoggle").click(function(){
        if ($(this).is(':checked')){

            $('.set1').attr("hidden",true);
            $('.set2').attr("hidden",false);
            console.log("red2")
            drawBars();
        }else{
            console.log("red")
            drawArea();
            $('.set1').attr("hidden",false);
            $('.set2').attr("hidden",true);
        }
    });

    $("#month1").on("change",(function(){
        drawBars();
    }));
    
    $("#month2").on("change",(function(){
        drawBars();
    }));

    $("#ord_fromdate").change(function(){
        fromtodatecheck();
        drawArea();   
    });
    
    $("#ord_todate").change(function(){
        fromtodatecheck();
        drawArea();   
    });

    $("#reset_clients").click(function(){
        if ($("#daymonthtoggle").is(':checked')){

        var date1 = new Date();

        var date2 = new Date();
        date2.setMonth(date1.getMonth()+1);

        var month = ("0" + (date1.getMonth())).slice(-2);
        var month2 = ("0" + (date2.getMonth())).slice(-2);

        var monthstring = month + "/" + date1.getFullYear();
        var monthstring2 = month2 + "/" + date2.getFullYear();

        $('#month1').val(monthstring);
        $('#month2').val(monthstring2);
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
    
        $('#ord_fromdate').val(datestring2);
        $('#ord_todate').val(datestring);
    
        drawArea();
    }
    });

    if ($("#daymonthtoggle").is(':checked')){
        $('.set1').attr("hidden",true);
        $('.set2').attr("hidden",false);
        drawBars();
    }else{
        $('.set1').attr("hidden",false);
        $('.set2').attr("hidden",true);
        drawArea();
    };
    
}

var date1 = new Date();
//date1.setMonth(date1.getMonth());

var date2 = new Date();
date2.setMonth(date1.getMonth()+1);

var month = ("0" + (date1.getMonth())).slice(-2);
var month2 = ("0" + (date2.getMonth())).slice(-2);

var monthstring = month + "/" + date1.getFullYear();
var monthstring2 = month2 + "/" + date2.getFullYear();

$('#month1').val(monthstring);
$('#month2').val(monthstring2);

var date3 = new Date();

date3.setDate(date3.getDate()-1)
date3.setMonth(date3.getMonth()+1)
var datestring = ("0" + (date3.getDate())).slice(-2)  + "-" + ("0" + (date3.getMonth())).slice(-2) + "-" + date3.getFullYear();

var date4 = new Date();
date4.setDate(date4.getDate()-30);
date4.setMonth(date4.getMonth()+1)
var datestring2 = ("0" + (date4.getDate())).slice(-2)  + "-" + ("0" + (date4.getMonth())).slice(-2) + "-" + date4.getFullYear();
console.log(datestring,datestring2)

$('#ord_fromdate').val(datestring2);
$('#ord_todate').val(datestring);
