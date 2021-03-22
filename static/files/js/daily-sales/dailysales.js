//var url='https://test.bleach-kw.com';
var url = 'https://my.bleachkw.com';
//var url = 'http://127.0.0.1:8000';

function monthlysales(){
    var sales_month = $('#calendar_month').val();
    console.log(sales_month,"war2")

    axios.get(url+'/api/daily-sales-list/',{ params: { 'sales_month': sales_month } })
    .then(function (response) {
        console.log(response.data,"war")

        //refresh table body
        $("#dailysaleslist").empty();

        $.each(response.data.list, function(key,value) {
            $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td class="generalclean align-right">'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td class="upholsteryclean align-right">'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td class="deepclean align-right">'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td class="carpetclean align-right">'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td class="kitchenclean align-right">'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td class="sterilizationclean align-right">'+parseFloat(value.Sterilization).toFixed(3)+'</td><td class="totalclean align-right">'+parseFloat(value.Total).toFixed(3)+'</td></tr>')
        })
        $('#dailysaleslist').append('<tr><td><b>Total</b></td><td></td><td id="generalsum" class="align-right"></td><td id="upholsterysum" class="align-right"></td><td id="deepsum" class="align-right"></td><td id="carpetsum" class="align-right"></td><td id="kitchensum" class="align-right"></td><td id="sterilizationsum" class="align-right"></td><td id="totalsum" class="align-right"></td></tr>');
        add_console();
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
    
  }