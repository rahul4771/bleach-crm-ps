$(".inv-coupon").hide();
//$(".inv-coupon-error").hide();
selectPayment('debit');
var cashcounter=false;
function addCoupon(){
  console.log($('.couponcode').val(),$('.orderId').val(),"runnns")
    

    $.ajax({
      url: "/customer/add-promocode",
      data: {
      'promocode': $('.couponcode').val(),'orderId':$('.orderId').val(),
      },
      dataType: "json",
      type: "GET",
      contentType: "application/json;charset=utf-8",
      
      success: function(data) {
          console.log(data.remainingamount,data.amount,data.alert,"all")

          if (data.amount > 0){
            $('.couponamount').text(data.amount);
            $('.finalamount').text(data.discount_amount);
            $('.beforecleaningamount').val(data.preamount);
            $('.preamount').text(data.preamount);
            $('.aftercleaningamount').val(data.postamount);
            $('.postamount').text(data.postamount);
            $('.evaluationtotalcost').val(data.evaluationtotalcost);
            $('.evaluationtotalamount').text(data.evaluationtotalcost);
            $('.remainingamount').text(data.remainingamount);
            $(".inv-coupon").show();
            $(".inv-coupon-code").hide();
          }

          if (data.alert == 'Invalid'){
            $('.couponcode').val('');
            $('.inv-coupon-error').attr("hidden",false);
            $('.inv-coupon-error').text("Invalid Coupon. Please Try Again !");
          }

          if (data.alert == 'expired'){
            $('.couponcode').val('');
            $('.inv-coupon-error').attr("hidden",false);
            $('.inv-coupon-error').text("Coupon Expired !");
          }

          if (data.alert == 'exists'){
            $('.couponcode').val('');
            $('.inv-coupon-error').attr("hidden",false);
            $('.inv-coupon-error').text("This order already has a coupon applied !");
          }

      }

})
}

function proceedInvoice(){
  
  if($('#inv-debit').hasClass('inv-payment-card-active')){
   
    $('#debit-form').submit();
   
  }
  else{
  
    
    openCashModal()
  }
}
function nextStepCash(){
 
  $('#cash-step-2').hide();
  $('#cash-step-1').show();
}
function selectPayment(pay){
   if(pay=='debit')
   {
    $("#inv-debit").removeClass('inv-payment-card')
    $("#inv-debit").addClass('inv-payment-card-active')
    $("#inv-cash").removeClass('inv-payment-card-active')
    $("#inv-cash").addClass('inv-payment-card')
    $("#inv-credit").removeClass('inv-payment-card-active')
    $("#inv-credit").addClass('inv-payment-card')
    $("#inv-check-debit").show();
    $("#inv-check-credit").hide();
    $("#inv-check-cash").hide();
    $("#inv-debit-check-box").addClass('inv-check-box-active');
    $("#inv-cash-check-box").removeClass('inv-check-box-active');
    $("#inv-credit-check-box").removeClass('inv-check-box-active');
   /* $("#inv-knet").attr("src","./icons/knet-white.png");
    $("#inv-cash-img").attr("src","./icons/wallet.png");
    $("#inv-credit-img").attr("src","./icons/debit-card.png");*/
   
   }
   else{
     if(pay=='cash'){
      $("#inv-cash").removeClass('inv-payment-card')
      $("#inv-debit").removeClass('inv-payment-card-active')
      $("#inv-debit").addClass('inv-payment-card')
      $("#inv-cash").addClass('inv-payment-card-active')
      $("#inv-credit").removeClass('inv-payment-card-active')
      $("#inv-credit").addClass('inv-payment-card');
     /* $("#inv-knet").attr("src","./icons/knet-icon.png");
      $("#inv-cash-img").attr("src","./icons/wallet-white3.png");
      $("#inv-credit-img").attr("src","./icons/debit-card.png");*/
      $("#inv-check-cash").show();
      $("#inv-check-debit").hide();
    $("#inv-check-credit").hide();
    $("#inv-cash-check-box").addClass('inv-check-box-active');
    $("#inv-debit-check-box").removeClass('inv-check-box-active');
    $("#inv-credit-check-box").removeClass('inv-check-box-active');
     }
     else{
      $("#inv-credit").removeClass('inv-payment-card')
      $("#inv-debit").removeClass('inv-payment-card-active')
      $("#inv-debit").addClass('inv-payment-card')
      $("#inv-credit").addClass('inv-payment-card-active')
      $("#inv-cash").removeClass('inv-payment-card-active')
    $("#inv-cash").addClass('inv-payment-card')
    $("#inv-check-credit").show();
    $("#inv-check-debit").hide();
    $("#inv-check-cash").hide();
    $("#inv-credit-check-box").addClass('inv-check-box-active');
    $("#inv-debit-check-box").removeClass('inv-check-box-active');
    $("#inv-cash-check-box").removeClass('inv-check-box-active');
   /* $("#inv-knet").attr("src","./icons/knet-icon.png");
    $("#inv-cash-img").attr("src","./icons/wallet.png");
    $("#inv-credit-img").attr("src","./icons/credit-card-white.png");*/
     }
   
   }
}
function printDiv() {
  

    window.print();

}
/*function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
  }*/
  function googleTranslateElementInit() {
    new google.translate.TranslateElement({ pageLanguage: 'en', layout: google.translate.TranslateElement.InlineLayout.SIMPLE, autoDisplay: false,includedLanguages: 'ar,en' }, 'google_translate_element');
  }
  
  function translateLanguage(lang) {
    
   
    var language = $(".select-language").val();
    if(language=='Arabic'){
    
      $("html").css("direction","rtl");
    }
    else{
      $("html").css("direction","ltr");
    }
    googleTranslateElementInit();
    var $frame = $('.goog-te-menu-frame:first');
    if (!$frame.length) {
      alert("Error: Could not find Google translate frame.");
      return false;
    }
    $frame.contents().find('.goog-te-menu2-item span.text:contains(' + lang + ')').get(0).click();
    return false;
  }
  
  $(function(){
    $('.selectpicker').selectpicker();
  });
  $("#lang-selector").change(function(){
    if($(this).prop("checked") == true){
      $("html").attr({"lang":"ar"},{"xml:lang":"ar"});
       
       var lang='Arabic';
       $('#company-name').text('بليتش');
       $("html").css("direction","rtl");
     //  $(".inv-customer-details").css({"border-right":"20px solid #F3F3F3","border-left":"0px"});
       $(".inv-customer-details").addClass("offset-md-2");
       $(".inv-invoice-card").removeClass("offset-md-2");
      $(".inv-logo").attr("src","/static/files/images/customer/logo-arabic.png")
     //  $(".inv-price-card").css({"border-right": "20px solid #f2f2f2","border-left":"1px solid #E6E6E6"});
       $(".inv-text-left").css({"text-align": "right",});
       $(".inv-text-right").css({"text-align": "left",});
       $(".inv-add-coupon").css({"border-radius": "6px 0px 0px 6px"});
       $(".inv-input").css({"border-radius":" 0px 6px 6px 0px","border-left":"0px","border-right":"1px dashed #707070"});
       $(".inv-invoice").addClass("offset-md-9");
       $(".inv-translator").css({"margin-left":"0","margin-right":"auto"});
       $("#lang-label").html("Arabic");
       $(".inv-cp").removeClass("float-left");
       $(".inv-cp").addClass("float-right");
       
  /* Receipt*/
  $(".inv-receipt-customer-details").addClass("offset-md-2");     
  $(".inv-receipt-card").removeClass("offset-md-2");
  $(".inv-receipt-amount-details").removeClass("offset-md-1");     
       $(".inv-receipt-amount").addClass("offset-md-1");
       $(".inv-sender").addClass("offset-md-6");     
       $(".inv-receiver").removeClass("offset-md-6");
       $(".inv-receipt-print").css({"margin-left":"auto","margin-right":"10px"});
       $(".inv-receipt-download").css({"margin-right":"auto","margin-left":"10px"});
       
      /* quotation*/

      $('#qt-download').removeClass('offset-md-4');
      $('#qt-print').addClass('offset-md-4');
      $('.fb-company').removeClass('offset-md-2');
      $('.fb-header').addClass('offset-md-2');
      $('.fb-end-card').removeClass('offset-md-1');
      $('.fb-middle-card').addClass('offset-md-1');

       
    
    }else{
      var lang='English';

      $('#company-name').text('Bleach');
      $("html").css("direction","ltr");
      $(".inv-cp").addClass("float-left");
      $(".inv-cp").removeClass("float-right");
     // $(".inv-customer-details").css({"border-left":"20px solid #F3F3F3","border-right":"0px"});
       $(".inv-customer-details").removeClass("offset-md-2");
       $(".inv-invoice-card").addClass("offset-md-2");
       $(".inv-receipt-customer-details").removeClass("offset-md-3");     
       $(".inv-receipt-card").addClass("offset-md-2");
       $(".inv-invoice").removeClass("offset-md-9");
       $(".inv-logo").attr("src","/static/files/images/customer/logo.png")

      // $(".inv-price-card").css({"border-left": "20px solid #f2f2f2","border-right":"1px solid #E6E6E6"})
       $(".inv-text-left").css({"text-align": "left",})
       $(".inv-text-right").css({"text-align": "right",})
       $(".inv-add-coupon").css({"border-radius": "0px 6px 6px 0px"});
      
       $(".inv-input").css({"border-radius":" 0px 6px 6px 0px","border-right":"0px","border-left":"1px dashed #707070"});

       $(".inv-translator").css({"margin-right":"0","margin-left":"auto"});
       $("#lang-label").html("English");
       $("html").attr("lang","en");

       /* Receipt*/
       $(".inv-receipt-customer-details").removeClass("offset-md-2");     
       $(".inv-receipt-card").addClass("offset-md-2");
       $(".inv-receipt-amount-details").addClass("offset-md-1");     
       $(".inv-receipt-amount").removeClass("offset-md-1");
       $(".inv-sender").removeClass("offset-md-6");     
       $(".inv-receiver").addClass("offset-md-6");
       $(".inv-receipt-download").css({"margin-left":"auto","margin-right":"10px"});
       $(".inv-receipt-print").css({"margin-right":"auto","margin-left":"10px"});
       $('.fb-company').addClass('offset-md-2');
      $('.fb-header').removeClass('offset-md-2');
      $('.fb-end-card').addClass('offset-md-1');
      $('.fb-middle-card').removeClass('offset-md-1');
       
    }
    googleTranslateElementInit();
    var $frame = $('.goog-te-menu-frame:first');
    if (!$frame.length) {
      alert("Error: Could not find Google translate frame.");
      return false;
    }
    $frame.contents().find('.goog-te-menu2-item span.text:contains(' + lang + ')').get(0).click();
    return false;

});


  