var url='https://test.bleach-kw.com';
//var url = 'https://my.bleachkw.com';
//var url = 'http://127.0.0.1:8000';

$('document').ready(function(){
    
    if($('#salestoggle').is(':checked')){
        datatype = 'evaluator';
    }else{
        datatype = 'service';
    }
    
})

function monthlysales(){
    var sales_month = $('#calendar_month').val();
    console.log(sales_month,"war2")

    axios.get(url+'/api/daily-sales-list/',{ params: { 'sales_month': sales_month, 'datatype':datatype } })
    .then(function (response) {
        console.log(response.data.list3,"war")

        $('#month_name').text(response.data.month_name);

        //refresh table body
        $("#dailysaleslist").empty();

        const evaluator_names = []
        const evaluator_ids = []
        $.each(response.data.list2, function(key,value) {
            
            var evaluator_data =  value.split(/([0-9]+)/);
            evaluator_names.push(evaluator_data[0])
            evaluator_ids.push(evaluator_data[1])
        })

        //refresh table header
        if (response.data.datatype == 'evaluator'){           
            $("#salesheaders").empty();
            $('#salesheaders').append('<th>Date</th><th data-hide="phone,tablet">Day</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[0]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[1]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[2]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[3]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[4]+'</th><th data-hide="phone,tablet" class="align-right">'+evaluator_names[5]+'</th><th data-hide="phone,tablet" class="align-right">Total Amount</th>')
        }else{
            $("#salesheaders").empty();
            $('#salesheaders').append('<th>Date</th><th data-hide="phone,tablet">Day</th><th data-hide="phone,tablet" class="align-right">General Cleaning</th><th data-hide="phone,tablet" class="align-right">Upholstery Cleaning</th><th data-hide="phone,tablet" class="align-right">Deep Cleaning</th><th data-hide="phone,tablet" class="align-right">Carpet Cleaning</th><th data-hide="phone,tablet" class="align-right">Kitchen Cleaning</th><th data-hide="phone,tablet" class="align-right">Sterilization</th><th data-hide="phone,tablet" class="align-right">Total Amount</th><th data-hide="phone,tablet" class="align-right">Sales Status</th>')
        }

        $.each(response.data.list, function(key,value) {
            //console.log(value.evaluator[evaluator_ids[0]],"liss")
            console.log(response.data.list.values(),"dtxx")

            var salestatus = parseFloat(parseFloat(value.Total) - parseFloat(2000.000)).toFixed(3) ;

            if (response.data.datatype == 'service'){
                if (response.data.todate == value.Date){
                    $('#dailysaleslist').append('<tr class="sales_rows" bgcolor="#CCFFFF"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td></tr>')
                }else{
                    $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td></tr>')
                }
            }else{

                if (response.data.todate == value.Date){
                    //var evaluator1 = value.
                    $('#dailysaleslist').append('<tr class="sales_rows" bgcolor="#CCFFFF"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(0).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td></tr>')
                }else{
                    $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td></tr>')
                }
            }
        })

        //update table total row at bottom
        if (response.data.datatype == 'service'){
            $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td class="align-right">'+parseFloat(response.data.generalcleaning_month).toFixed(3)+'</td><td id="upholsterysum" class="align-right">'+parseFloat(response.data.upholsterycleaning_month).toFixed(3)+'</td><td id="deepsum" class="align-right">'+parseFloat(response.data.deepcleaning_month).toFixed(3)+'</td><td id="carpetsum" class="align-right">'+parseFloat(response.data.carpetcleaning_month).toFixed(3)+'</td><td id="kitchensum" class="align-right">'+parseFloat(response.data.kitchencleaning_month).toFixed(3)+'</td><td id="sterilizationsum" class="align-right">'+parseFloat(response.data.sterilization_month).toFixed(3)+'</td><td id="totalsum" class="align-right">'+parseFloat(response.data.cleaning_amount_month).toFixed(3)+'</td><td id="totalsales" class="align-right">'+parseFloat(response.data.cleaning_amount_month - 52000).toFixed(3)+'</td></tr>');
        }else{
            $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td class="align-right">'+parseFloat(response.data.generalcleaning_month).toFixed(3)+'</td><td id="upholsterysum" class="align-right">'+parseFloat(response.data.upholsterycleaning_month).toFixed(3)+'</td><td id="deepsum" class="align-right">'+parseFloat(response.data.deepcleaning_month).toFixed(3)+'</td><td id="carpetsum" class="align-right">'+parseFloat(response.data.carpetcleaning_month).toFixed(3)+'</td><td id="kitchensum" class="align-right">'+parseFloat(response.data.kitchencleaning_month).toFixed(3)+'</td><td id="sterilizationsum" class="align-right">'+parseFloat(response.data.sterilization_month).toFixed(3)+'</td><td id="totalsum" class="align-right">'+parseFloat(response.data.cleaning_amount_month).toFixed(3)+'</td></tr>');
        }

        //adding up and down arrows in sales list table
        $('.salestatus').each(function(){

            var salestatus = $(this).text();
            console.log(salestatus,"stats")

            if (salestatus < 0){
                $(this).text(parseFloat(Math.abs(salestatus)).toFixed(3));
                $(this).append(' <i class="fa fa-arrow-down" aria-hidden="true" style="color:#ec6262;"></i>');
                $(this).addClass('red-text');
            }else if (salestatus > 0){
                $(this).append(' <i class="fa fa-arrow-up" aria-hidden="true" style="color:#3cbbb1;"></i>');
                $(this).addClass('green-text');
            }else{
                console.log("zero")
            }
        
        });

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