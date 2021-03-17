var url='https://test.bleach-kw.com';
//var url = 'https://my.bleachkw.com';
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
            $('#dailysaleslist').append('<tr class="sales_rows"><td>'+value.Date+'</td><td>'+value.Day+'</td><td>'+parseFloat(value.GeneralCleaning).toFixed(3)+'</td><td>'+parseFloat(value.UpholsteryCleaning).toFixed(3)+'</td><td>'+parseFloat(value.DeepCleaning).toFixed(3)+'</td><td>'+parseFloat(value.CarpetCleaning).toFixed(3)+'</td><td>'+parseFloat(value.KitchenCleaning).toFixed(3)+'</td><td>'+parseFloat(value.Sterilization).toFixed(3)+'</td><td>'+parseFloat(value.Total).toFixed(3)+'</td></tr>')
        })
    })
}