var doc = new jsPDF();
var specialElementHandlers = {
    '#editor': function (element, renderer) {
        return true;
    }
};

$('#download').click(async function () {
  
       
        let scrollPromise = new Promise(function(myResolve, myReject) {
            // "Producing Code" (May take some time)
            window.scrollTo(0, 0);
              myResolve(); // when successful
              myReject();  // when error
            });
            scrollPromise.then(function () {
                var doc = new jsPDF();
    var vp = document.getElementById("viewportMeta").getAttribute("content");

    document.getElementById("viewportMeta").setAttribute("content", "width=1280");
    html2canvas($('.inv-card'),{
        useCORS : true,
        logging: true, letterRendering: 1,
        allowTaint:false,
        onrendered:function(canvas){
     
        var img=canvas.toDataURL("image/png");
       
       
        doc.addImage(img, 'PNG',10,10,190,180);
        
      
        doc.save('invoice.pdf');
        document.getElementById("viewportMeta").setAttribute("content", vp);
        }
     
        })
            })
     
       
       
    
        
       
   
});






    
    // "Consuming Code" (Must wait for a fulfilled Promise)
    myPromise.then(
      function(value) { /* code if successful */ },
      function(error) { /* code if some error */ }
    );