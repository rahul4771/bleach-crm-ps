
   window.onclick = function(event) {
     if (event.target ==  $('#bk-approve')) {
       $('#termsModal').hide();
     }
     if (event.target ==  $('#bk-reject')) {
      $('#rejectModal').hide();
    }
   }

   function openModal(){  
        $('#termsModal').show();    
   }
   function openVisit(){  
    $('#visitModal').show();    
}
function closeVisit(){  
  $('#visitModal').hide();    
}
   function closeModal(){  
    $('#termsModal').hide();    
}
function openRejectModal(){  
  $('#rejectModal').show();    
}
function closeRejectModal(){  
  $('#rejectModal').hide();    
}
function openCashModal(){  
  $('#cashModal').show();    
}
function closeCashModal(){  
  $('#cashModal').hide(); 
  $('#cash-step-1').hide();
  $('#cash-step-2').show();
  
}
function openDetailsModal(elem){
  id = $(elem).data('popup_id');
  $('#detailsModal'+id).show(); 
  
}
function closeDetailsModal(elem){
  id = $(elem).data('popup_id');
  $('#detailsModal'+id).hide(); 
}
function openPaymentModal(){
  $('#paymentModal').show()
  
}
function closePaymentModal(){
  $('#paymentModal').hide()
  
}