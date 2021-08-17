//var url='https://test.bleach-kw.com';
//var url = 'https://my.bleachkw.com';
//var url = 'http://127.0.0.1:8000';
var url = api;
  

$('document').ready(function(){
    if($('#salestoggle').is(':checked')){
        datatype = 'evaluator';
    }else{
        datatype = 'service';
    }

    var date1 = new Date();

    var month = ("0" + (date1.getMonth()+1)).slice(-2);
    console.log(month,"lp")

    var datestring = month + "/" + date1.getFullYear();
    $('#calendar_month').val(datestring);
    
})

function nextDay(){
    var a = $('#model_date').text().split('-');
    console.log(a);
      
    var tmpSelectedDay   = new Date(a[1]+'/'+ a[0]+'/' +a[2]);
    console.log(tmpSelectedDay)
    tmpSelectedDay.setDate(tmpSelectedDay.getDate() + 1);
    var d = moment(tmpSelectedDay).format('DD-MM-YYYY')
    $('#model_date').text(d);
    $('#model_date2').text(d);

    //daily sales api fetch for single day
    axios.get(url+'/api/daily-sales-breakdown-list/',{ params: { 'sales_date': d } })
    .then(function (response) {
        console.log(response.data.total_day_sales,"salelis")

        if (response.data.list.length > 0){
            $("#model-table tr:not(:first)").remove(); 
            $('#sales_status').html('');

            $.each(response.data.list,function(key,value){
                $('#model-table').append('<tr><td>'+value.order_no+'</td><td>'+value.customer+'</td><td>'+value.payment_policy+'</td><td  style="text-align: right;">'+parseFloat(value.net_amount).toFixed(3)+'</td><td>'+value.service_type+'</td><td>'+value.salesman+'</td></tr>');
            })

            $('#total_day_sale').text(parseFloat(response.data.total_day_sales).toFixed(3));
            $('#sale_day').text(response.data.day);
            
            if (response.data.sales_status < 2000){
                $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                $('#sales_status').attr('style','color:#ec6262;');
            }else{
                $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
                $('#sales_status').attr('style','color:#3cbbb1;');
            }

        }else{
            $("#model-table tr:not(:first)").remove(); 
            $('#total_day_sale').text('000.000');
            $('#sales_status').html('');
            $('#sales_status').append('000.000 <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
            $('#sale_day').text(response.data.day);
        }

    })

}

function prevDay(){.0
    var a = $('#model_date').text().split('-');
    console.log(a);
      
    var tmpSelectedDay   = new Date(a[1]+'/'+ a[0]+'/' +a[2]);
     console.log(tmpSelectedDay)
    tmpSelectedDay.setDate(tmpSelectedDay.getDate() - 1);
    var d = moment(tmpSelectedDay).format('DD-MM-YYYY')
    $('#model_date').text(d);
    $('#model_date2').text(d);


    //daily sales api fetch for single day
    axios.get(url+'/api/daily-sales-breakdown-list/',{ params: { 'sales_date': d } })
    .then(function (response) {
        console.log(response.data.total_day_sales,"salelis")

        if (response.data.list.length > 0){
            $("#model-table tr:not(:first)").remove(); 
            $('#sales_status').html('');

            $.each(response.data.list,function(key,value){
                $('#model-table').append('<tr><td>'+value.order_no+'</td><td>'+value.customer+'</td><td>'+value.payment_policy+'</td><td  style="text-align: right;">'+parseFloat(value.net_amount).toFixed(3)+'</td><td>'+value.service_type+'</td><td>'+value.salesman+'</td></tr>');
            })

            $('#total_day_sale').text(parseFloat(response.data.total_day_sales).toFixed(3));
            $('#sale_day').text(response.data.day);
            
            if (response.data.sales_status < 2000){
                $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                $('#sales_status').attr('style','color:#ec6262;');
            }else{
                $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
                $('#sales_status').attr('style','color:#3cbbb1;');
            }

        }else{
            $("#model-table tr:not(:first)").remove(); 
            $('#total_day_sale').text('000.000');
            $('#sales_status').html('');
            $('#sales_status').append('000.000 <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
            $('#sale_day').text(response.data.day);
        }

    })

}

function showModal(dd){
// console.log(d,"saleda")
// console.log($(d).attr("data-d"))
    var tmpSelectedDay     = $(dd).attr("data-d")
    var d = moment(tmpSelectedDay).format('DD-MM-YYYY') //tmpSelectedDay.toString()    

    $('#model_date').text(d);
    $('#model_date2').text(d);

    console.log(d)
    console.log( $('#id_model_button'));
      $('#id_model_button').click();
      //$('#detialsModel').modal('show');

      //daily sales api fetch for single day
      axios.get(url+'/api/daily-sales-breakdown-list/',{ params: { 'sales_date': d } })
        .then(function (response) {
            console.log(response.data.total_day_sales,"salelis")

            if (response.data.list.length > 0){
                $("#model-table tr:not(:first)").remove(); 
                $('#sales_status').html('');

                $.each(response.data.list,function(key,value){
                    $('#model-table').append('<tr><td>'+value.order_no+'</td><td>'+value.customer+'</td><td>'+value.payment_policy+'</td><td  style="text-align: right;">'+parseFloat(value.net_amount).toFixed(3)+'</td><td>'+value.service_type+'</td><td>'+value.salesman+'</td></tr>');
                })

                $('#total_day_sale').text(parseFloat(response.data.total_day_sales).toFixed(3));
                $('#sale_day').text(response.data.day);
                
                if (response.data.sales_status < 2000){
                    $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                    $('#sales_status').attr('style','color:#ec6262;');
                }else{
                    $('#sales_status').append(parseFloat(response.data.sales_status).toFixed(3) + '<i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
                    $('#sales_status').attr('style','color:#3cbbb1;');
                }

            }else{
                $("#model-table tr:not(:first)").remove(); 
                $('#total_day_sale').text('000.000');
                $('#sales_status').html('');
                $('#sales_status').append('000.000 <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                $('#sale_day').text(response.data.day);
            }
    
        })
  }
  

function monthlysales(){
    
    var sales_month = $('#calendar_month').val();

    axios.get(url+'/api/daily-sales-list/',{ params: { 'sales_month': sales_month, 'datatype':datatype } })
    .then(function (response) {

        $('#month_name').text(response.data.month_name);

        //refresh table body
        $("#dailysaleslist").empty();

        const evaluator_names = []
        $.each(response.data.list2, function(key,value) {
            
            var evaluator_data =  value.split(/([0-9]+)/);
            evaluator_names.push(evaluator_data[0])
        })

        //refresh table header
        if (response.data.datatype == 'evaluator'){           
            $("#salesheaders").empty();
            $('#salesheaders').append('<th>Date</th><th data-hide="phone,tablet">Day</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[0]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[1]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[2]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[3]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[4]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[5]+'</th><th data-hide="phone,tablet" class="align-right">Others</th><th data-hide="phone,tablet" class="align-right">Total Amount</th> <th class="align-center">Action</th>')
            
        }else{
            $("#salesheaders").empty();
            $('#salesheaders').append('<th>Date</th><th data-hide="phone,tablet">Day</th><th data-hide="phone,tablet" class="align-right">Detailed Cleaning</th><th data-hide="phone,tablet" class="align-right">Special Care</th><th data-hide="phone,tablet" class="align-right">Kitchen Cleaning</th><th data-hide="phone,tablet" class="align-right">Infection Control</th><th data-hide="phone,tablet" class="align-right">Total Amount</th><th data-hide="phone,tablet" class="align-right">Sales Status</th><th class="align-center">Action</th>')
           
        }
       
        $('.footable').trigger('footable_resize');

        //monthly evaluator total amount calculation
        var evaluator1 = 0 ;
        var evaluator2 = 0 ;
        var evaluator3 = 0 ;
        var evaluator4 = 0 ;
        var evaluator5 = 0 ;
        var evaluator6 = 0 ;
        $.each(response.data.list3, function(key,value) { 

            if (response.data.list2[0] in value){
                evaluator1 += parseFloat(value[""+response.data.list2[0]+""]);
            }

            if (response.data.list2[1] in value){
                evaluator2 += parseFloat(value[""+response.data.list2[1]+""]);
            }

            if (response.data.list2[2] in value){
                evaluator3 += parseFloat(value[""+response.data.list2[2]+""]);
            }

            if (response.data.list2[3] in value){
                evaluator4 += parseFloat(value[""+response.data.list2[3]+""]);
            }

            if (response.data.list2[4] in value){
                evaluator5 += parseFloat(value[""+response.data.list2[4]+""]);
            }

            if (response.data.list2[5] in value){
                evaluator6 += parseFloat(value[""+response.data.list2[5]+""]);
            }
        })

        var others = 0;
        //looping through main list and adding items to table body
        $.each(response.data.list, function(key,value) {  
            
            var salestatus = parseFloat(parseFloat(value.Total) - parseFloat(2000.000)).toFixed(3) ;

            //checking service or evauator mode
            if (response.data.datatype == 'service'){
                    var salesdate = String(value.Date);
                if (response.data.todate == value.Date){
                    $('#dailysaleslist').append('<tr class="sales_rows" bgcolor="#CCFFFF"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.DetailedCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.SpecialCare).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.InfectionControl).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td> <td data-d="'+salesdate+'" onclick="showModal(this)" class="align-center pointer" style="color:#2e4e85;">Daily Breakdown</td> </tr>')
                }else{
                    var salesdate = String(value.Date);
                    console.log(salesdate,"fpr")
                    $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.DetailedCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.SpecialCare).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.InfectionControl).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td><td data-d="'+salesdate+'" onclick="showModal(this)" class="align-center pointer" style="color:#2e4e85;">Daily Breakdown</td></tr>')
                }
            }else{

                others += parseFloat(value.others);

                if (response.data.todate == value.Date){
                    $('#dailysaleslist').append('<tr class="sales_rows" bgcolor="#CCFFFF"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value[""+response.data.list2[0]+""]).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value[""+response.data.list2[1]+""]).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value[""+response.data.list2[2]+""]).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value[""+response.data.list2[3]+""]).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value[""+response.data.list2[4]+""]).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value[""+response.data.list2[5]+""]).toFixed(3)+'</td><td class="align-right">'+parseFloat(value.others).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="align-right">Daily BreakDown</td></tr>')
                }else{
                    $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value[""+response.data.list2[0]+""]).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value[""+response.data.list2[1]+""]).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value[""+response.data.list2[2]+""]).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value[""+response.data.list2[3]+""]).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value[""+response.data.list2[4]+""]).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value[""+response.data.list2[5]+""]).toFixed(3)+'</td><td class="align-right">'+parseFloat(value.others).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="align-right">Daily BreakDown</td></tr>')
                }
            }
        })
       
      
        //update table total row at bottom
        $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td class="align-right">'+parseFloat(response.data.detailed_cleaning_month).toFixed(3)+'</td><td id="upholsterysum" class="align-right">'+parseFloat(response.data.special_care_month).toFixed(3)+'</td><td id="deepsum" class="align-right">'+parseFloat(response.data.kitchen_cleaning_month).toFixed(3)+'</td><td id="carpetsum" class="align-right">'+parseFloat(response.data.infection_control_month).toFixed(3)+'</td><td id="totalsum" class="align-right">'+parseFloat(response.data.cleaning_amount_month).toFixed(3)+'</td><td id="totalsales" class="align-right">'+parseFloat(response.data.cleaning_amount_month - 52000).toFixed(3)+'</td><td></td></tr>');

        // if (response.data.datatype == 'service'){
        //     $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td class="align-right">'+parseFloat(response.data.generalcleaning_month).toFixed(3)+'</td><td id="upholsterysum" class="align-right">'+parseFloat(response.data.upholsterycleaning_month).toFixed(3)+'</td><td id="deepsum" class="align-right">'+parseFloat(response.data.deepcleaning_month).toFixed(3)+'</td><td id="carpetsum" class="align-right">'+parseFloat(response.data.carpetcleaning_month).toFixed(3)+'</td><td id="kitchensum" class="align-right">'+parseFloat(response.data.kitchencleaning_month).toFixed(3)+'</td><td id="sterilizationsum" class="align-right">'+parseFloat(response.data.sterilization_month).toFixed(3)+'</td><td id="totalsum" class="align-right">'+parseFloat(response.data.cleaning_amount_month).toFixed(3)+'</td><td id="totalsales" class="align-right">'+parseFloat(response.data.cleaning_amount_month - 52000).toFixed(3)+'</td></tr>');
        // }else{
        //     $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td class="align-right">'+parseFloat(evaluator1).toFixed(3)+'</td><td id="upholsterysum" class="align-right">'+parseFloat(evaluator2).toFixed(3)+'</td><td id="deepsum" class="align-right">'+parseFloat(evaluator3).toFixed(3)+'</td><td id="carpetsum" class="align-right">'+parseFloat(evaluator4).toFixed(3)+'</td><td id="kitchensum" class="align-right">'+parseFloat(evaluator5).toFixed(3)+'</td><td id="sterilizationsum" class="align-right">'+parseFloat(evaluator6).toFixed(3)+'</td><td id="sterilizationsum" class="align-right">'+parseFloat(others).toFixed(3)+'</td><td id="totalsum" class="align-right">'+parseFloat(response.data.cleaning_amount_month).toFixed(3)+'</td></tr>');
        // }

        //adding up and down arrows in sales list table and amount color change
        $('.salestatus').each(function(){

            var salestatus = $(this).text();
            console.log(salestatus,"stats")

            if (salestatus < 0){
                $(this).text(parseFloat(Math.abs(salestatus)).toFixed(3));
                $(this).append(' <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                $(this).addClass('red-text');
                $(this).parents('tr').find("td:first").addClass('red-line');
            }else if (salestatus > 0){
                $(this).append(' <i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
                $(this).addClass('green-text');
                $(this).parents('tr').find("td:first").addClass('green-line');
            }else{
                console.log("zero")
            }
        
        });

        //monthly amount color change 
        var monthlytotalsales = $('#totalsales').text();

        if (monthlytotalsales < 0){
            $('#totalsales').text(parseFloat(Math.abs(monthlytotalsales)).toFixed(3));
            $('#totalsales').append(' <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
            $('#totalsales').addClass('red-text');
        }else if (monthlytotalsales > 0){
            $('#totalsales').append(' <i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
            $('#totalsales').addClass('green-text');
        }else{
            console.log("zero")
        }
       // $('.footable').trigger('footable_resize');
       $('#salesTable').footable();
        $('#salesTable').trigger('footable_redraw');
        // jQuery(function() {  
        //     jQuery('#salesTable').footable();  
        //    });  
        

         
      

        
    })
   
    
  

}


$('#salestoggle').click(function(){
    if($(this).is(':checked')){
        datatype = 'evaluator';
        monthlysales();
    }else{
        datatype = 'service';
        monthlysales();
    }
})