
var doc = new jsPDF();
var specialElementHandlers = {
    '#editor': function (element, renderer) {
        return true;
    }
};

$('#download').click(function () {
    var doc = new jsPDF();
    var vp = document.getElementById("viewportMeta").getAttribute("content");

    document.getElementById("viewportMeta").setAttribute("content", "width=1280");
    html2canvas($('.inv-card'),{
        useCORS : true,
        logging: true, letterRendering: 1,
        allowTaint:false,
        onrendered:function(canvas){
     
        var img=canvas.toDataURL("image/png");
       
       
        doc.addImage(img, 'PNG',10,10,190,200);
        
      
        doc.save('invoice.pdf');
        document.getElementById("viewportMeta").setAttribute("content", vp);
        }
     
        })
       
    
        
       
   
});





