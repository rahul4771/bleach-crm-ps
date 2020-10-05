function salestarget(evaluator_id){
    console.log(evaluator_id,"evid")
    
    //sales target chart
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
            },
            animation: {
                duration: 1000,
                easing: 'out'
            },
            legend:{position:'none'}
        };
        
        chart.setOptions(options);
        
        function drawBars() {
            var dom = 'Month' ;
            var month_1 = $('#sales_target_month1').val();
            var month_2 = $('#sales_target_month2').val();

            console.log(month_1, month_2, evaluator_id,"monthd2")

            const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
            ];

            $.ajax({
                url: '/bleach_admin/ajax/sales-target-data/',
                data: {
                'fromdate': month_1,'todate':month_2, 'dom':dom, 'evaluator':evaluator_id
                },
                dataType: "json",
                type: "GET",
                contentType: "application/json;charset=utf-8",
                
                success: function(data_month) {
                console.log('lp')
                var sales = [['Date', 'Amount']];
                var sale_sum = 0;
                var total_sum = 0;
                
                if(data_month.length > 0){
                    $.each(data_month,function(key,value){
                        console.log(value.date,"uio")
                        var vals = value.date.split('-');
                        var year = parseInt(vals[0]);
                        var month = parseInt (vals[1]);
                        var day = parseInt (vals[2]);
                        const d2 = new Date(year,month-1,day);
                        sales.push([monthNames[d2.getMonth()],value.amount]);
                        sale_sum += parseFloat(value.amount);
                        total_sum += parseFloat(value.total);
                    });
                }else{
                    sales.push(['',0]);
                    sale_sum = 0;
                    total_sum = 0;
                }
                console.log(sales,"sls")
                $('#total_sales2').text(sale_sum);
                $('#total_orders2').text(total_sum);


                data[0] = new google.visualization.arrayToDataTable(sales);

                chart.setChartType('ColumnChart');
                chart.setDataTable(data[0]);
                chart.draw();
            }
            });
        }

        function drawArea() {

            var dom = 'Date' ;
            var fromd = $('#sales_target_date1').val();
            var to = $('#sales_target_date2').val();

            var fromdate= fromd.split("-").reverse().join("-");
            var todate= to.split("-").reverse().join("-");
            console.log(fromdate,todate,'pp')

            $.ajax({
                url: '/bleach_admin/ajax/sales-target-data/',
                data: {
                'fromdate': fromdate,'todate':todate, 'dom':dom, 'evaluator':evaluator_id
                },
                dataType: "json",
                type: "GET",
                contentType: "application/json;charset=utf-8",
                
                success: function(data_date) {
                console.log('lp')
                var sales = [['Date', 'Amount']];
                var sale_sum = 0;
                var total_sum = 0;
                
                if(data_date.length > 0){
                    $.each(data_date,function(key,value){
                        console.log(value.date,"uio")
                        var vals = value.date.split('-');
                        var year = parseInt(vals[0]);
                        var month = parseInt (vals[1]);
                        var day = parseInt (vals[2]);
                        
                        sales.push([new Date(year,month-1,day),value.amount]);
                        sale_sum += parseInt(value.amount);
                        total_sum += parseInt(value.total);
                    });
                }else{
                    sales.push(['',0]);
                    sale_sum = 0;
                    total_sum = 0;
                }
                console.log(sales,"sls")
                $('#total_sales2').text(sale_sum);
                $('#total_orders2').text(total_sum);

                data[1] = new google.visualization.arrayToDataTable(sales);

                chart.setChartType('AreaChart');
                chart.setDataTable(data[1]);
                chart.draw();
            }
            });
        }
        
        $("#daymonth_sales_target").click(function(){
            if ($(this).is(':checked')){
                console.log("red")
                drawArea();
                $('.targetset1').attr("hidden",false);
                $('.targetset2').attr("hidden",true);
            }else{
                $('.targetset1').attr("hidden",true);
                $('.targetset2').attr("hidden",false);
                console.log("red2")
                drawBars();
            }
        });

        $("#sales_target_month1").on("change",(function(){
            drawBars();
        }));
        
        $("#sales_target_month2").on("change",(function(){
            drawBars();
        }));

        $("#sales_target_date1").change(function(){
            drawArea();   
        });
        
        $("#sales_target_date2").change(function(){
            drawArea();   
        });

        $("#reset_sales_target").click(function(){
            if ($("#daymonth_sales_target").is(':checked')){
            var date1 = new Date();
            var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();
        
            var date2 = new Date();
            date2.setDate(date2.getDate()-30);
            var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
            console.log(datestring,datestring2)
        
            $('#sales_target_date1').val(datestring2);
            $('#sales_target_date2').val(datestring);
        
            drawArea();
        }else{
            var date1 = new Date();
            var month = ("0" + (date1.getMonth()-1)).slice(-2);
            var month2 = ("0" + (date1.getMonth())).slice(-2);
            console.log(month,"lp")
            var datestring = month + "/" + date1.getFullYear();
            var datestring2 = month2 + "/" + date1.getFullYear();

            $('#sales_target_month1').val(datestring);
            $('#sales_target_month2').val(datestring2);
            drawBars();
        }
        });

        if ($("#daymonth_sales_target").is(':checked')){
            $('.targetset1').attr("hidden",false);
            $('.targetset2').attr("hidden",true);
            drawArea();
        }else{
            $('.targetset1').attr("hidden",true);
            $('.targetset2').attr("hidden",false);
            drawBars();
        };
        
    }

    var date1 = new Date();
    var month = ("0" + (date1.getMonth()-1)).slice(-2);
    var month2 = ("0" + (date1.getMonth())).slice(-2);
    console.log(month,"lp")
    var datestring = month + "/" + date1.getFullYear();
    var datestring2 = month2 + "/" + date1.getFullYear();

    $('#sales_target_month1').val(datestring);
    $('#sales_target_month2').val(datestring2);

    var datestring = date1.getDate()-1  + "-" + (date1.getMonth()+1) + "-" + date1.getFullYear();

    var date2 = new Date();
    date2.setDate(date2.getDate()-60);
    var datestring2 = date2.getDate()  + "-" + (date2.getMonth()+1) + "-" + date2.getFullYear();
    console.log(datestring,datestring2)

    $('#sales_target_date1').val(datestring2);
    $('#sales_target_date2').val(datestring);

}