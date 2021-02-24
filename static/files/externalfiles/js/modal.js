
   window.onclick = function(event) {
     if (event.target ==  $('#bk-approve')) {
       $('#termsModal').hide();
     }
   }

   function openModal(){  
        $('#termsModal').show();    
   }
   function closeModal(){  
    $('#termsModal').hide();    
}