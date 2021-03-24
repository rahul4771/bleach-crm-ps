var url='https://test.bleach-kw.com';
//var url = 'https://my.bleachkw.com';
//var url = 'http://127.0.0.1:8000';

function monthlysales(){
    var sales_month = $('#calendar_month').val();
    console.log(sales_month,"war2")

    axios.get(url+'/api/daily-sales-list/',{ params: { 'sales_month': sales_month } })
    .then(function (response) {
        console.log(response.data,"war")

        $('#month_name').text(response.data.month_name);

        //refresh table body
        $("#dailysaleslist").empty();

        $.each(response.data.list, function(key,value) {
            console.log(response.data.todate,value.Date,"dtsss")

            var salestatus = parseFloat(parseFloat(value.Total) - parseFloat(2000.000)).toFixed(3) ;

            if (response.data.todate == value.Date){
                $('#dailysaleslist').append('<tr class="sales_rows" bgcolor="#CCFFFF"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td></tr>')
            }else{
                $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td><td class="salestatus align-right">'+salestatus+'</td></tr>')
            }

        })
        $('#dailysaleslist').append('<tr bgcolor="#ececec"><td><b>Total</b></td><td></td><td id="generalsum" class="align-right"></td><td id="upholsterysum" class="align-right"></td><td id="deepsum" class="align-right"></td><td id="carpetsum" class="align-right"></td><td id="kitchensum" class="align-right"></td><td id="sterilizationsum" class="align-right"></td><td id="totalsum" class="align-right"></td><td id="totalsales" class="align-right"></td></tr>');
        add_console();

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
    })

}

function add_console(){
  console.log("oatu")
    var sum1 = 0;
    var sum2 = 0;
    var sum3 = 0;
    var sum4 = 0;
    var sum5 = 0;
    var sum6 = 0;
    var sum7 = 0;
    var sum8 = 0;

    $('.generalclean').each(function(){
        sum1 += parseFloat($(this).text());
    });

    $('.upholsteryclean').each(function(){
        sum2 += parseFloat($(this).text());
    });

    $('.deepclean').each(function(){
        sum3 += parseFloat($(this).text());
    });

    $('.carpetclean').each(function(){
        sum4 += parseFloat($(this).text());
    });

    $('.kitchenclean').each(function(){
        sum5 += parseFloat($(this).text());
    });

    $('.sterilizationclean').each(function(){
        sum6 += parseFloat($(this).text());
    });

    $('.totalclean').each(function(){
        sum7 += parseFloat($(this).text());
    });

    console.log(sum1, sum2,sum3,sum4,sum5,sum6,sum7,"lol")
    
    document.getElementById('generalsum').innerHTML =  parseFloat(sum1).toFixed(3) ;
    document.getElementById('upholsterysum').innerHTML =  parseFloat(sum2).toFixed(3) ;
    document.getElementById('deepsum').innerHTML =  parseFloat(sum3).toFixed(3) ;
    document.getElementById('carpetsum').innerHTML =  parseFloat(sum4).toFixed(3) ;
    document.getElementById('kitchensum').innerHTML =  parseFloat(sum5).toFixed(3) ;
    document.getElementById('sterilizationsum').innerHTML =  parseFloat(sum6).toFixed(3) ;
    document.getElementById('totalsum').innerHTML =  parseFloat(sum7).toFixed(3) ;
    document.getElementById('totalsales').innerHTML =  parseFloat(sum7 - 52000).toFixed(3) ;

    var monthlytotalsales = $('#totalsales').text();
    console.log(monthlytotalsales,"stats")

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
    
  }