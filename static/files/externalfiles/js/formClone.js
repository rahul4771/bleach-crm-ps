var counter = 1;


/* Clone Form*/
 function addItem(){
        
      
        var el = $('#bk-item-1').clone().attr({'id': 'bk-item-' + ++counter}).appendTo('#bk-main-form');
       
        $('#bk-item-'+counter).find('#bk-title-1').attr('id', 'bk-title-'+counter);  /*To change title id */
        
       
        $('#bk-item-'+counter).find('#bk-del-btn-1').attr('id', 'bk-del-btn-'+counter);
        $('#bk-title-'+counter).html($(".bk-select").val().split(' ')[0]+' '+counter); /* To change title */
        $('#bk-item-'+counter).find('#bk-size-1').attr({'id': 'bk-size-'+counter,'name': 'bk-size-'+counter}).val(''); /*To change name & id of size*/ 
        $('#bk-item-'+counter).find('#bk-age-1').attr({'id': 'bk-age-'+counter,'name': 'bk-age-'+counter}).val(''); /*To change name & id of age*/
        $('#bk-item-'+counter).find("#bk-material-1").attr({'id': 'bk-material-'+counter,'name': 'bk-material-'+counter}).val(''); /*To change name of material*/
        $('#bk-item-'+counter).find("#bk-color-1").attr({'id': 'bk-color-'+counter,'name': 'bk-color-'+counter}).val(''); /*To change name of color*/
        $('#bk-item-'+counter).find('#bk-stain-1-1').attr({'id': 'bk-stain-'+counter+'-1','name': 'bk-stain-'+counter}); /*To change name & id of stain (yes)*/
        $('#bk-item-'+counter).find('#bk-stain-1-2').attr({'id': 'bk-stain-'+counter+'-2','name': 'bk-stain-'+counter}); /*To change name & id of stain (no) */
        $('#bk-item-'+counter).find("#bk-stain-reason-1").attr({'id': 'bk-stain-reason-'+counter,'name': 'bk-stain-reason-'+counter}).val(''); /*To change name of reason for stain*/
        $("#bk-material-"+counter).removeClass("chzn-done").css("display", "block").next().remove();
        $("#bk-material"+counter).addClass('chosen-select');
        
        $("#bk-color-"+counter).removeClass("chzn-done").removeAttr("id").css("display", "block").next().remove();
        $("#bk-color"+counter).addClass('chosen-select');
        $("#bk-stain-reason-"+counter).removeClass("chzn-done").removeAttr("id").css("display", "block").next().remove();
        $("#bk-stain-reason"+counter).addClass('chosen-select');
        $('.chosen-select').chosen();
        $('#bk-del-btn-'+counter).show()

        $('#sectioncounter_id').val(counter);
 }


 /* Remove Form*/

 function removeDiv(elem){
      /* To find Children */
    
    var childDiv = [];
    $("#bk-main-form > div").each((index, elem) => {
        childDiv.push(elem.id);
   });
    if ($(elem).parent('div').attr('id') != 'bk-item-1')
    $(elem).parent('div').remove();
    var elementId=$(elem).parent('div').attr('id');
    var currentVal=elementId.split('-')[2]; /* value of current item index*/
   if(currentVal<childDiv.length){

   
   var nextVal=parseInt(currentVal)+1;
   var currentVal=parseInt(currentVal);
    $('#bk-title-'+nextVal).attr('id', 'bk-title-'+currentVal);
    $('#bk-del-btn-'+nextVal).attr('id', 'bk-del-btn-'+currentVal);
    $('#bk-del-btn-'+currentVal).show()
    $('#bk-title-'+currentVal).html($(".bk-select").val().split(' ')[0]+' '+currentVal); /* To change title */
    $('#bk-size-'+nextVal).attr({'id': 'bk-size-'+currentVal,'name': 'bk-size-'+currentVal});
    $('#bk-age-'+nextVal).attr({'id': 'bk-age-'+currentVal,'name': 'bk-age-'+currentVal});
    $('#bk-material-'+nextVal).attr({'id': 'bk-material-'+currentVal,'name': 'bk-material-'+currentVal});
    $('#bk-color-'+nextVal).attr({'id': 'bk-color-'+currentVal,'name': 'bk-color-'+currentVal});
    $('#bk-stain-'+nextVal+'-1').attr({'id': 'bk-stain-'+currentVal+'-1','name': 'bk-stain-'+currentVal});
    $('#bk-stain-'+nextVal+'-2').attr({'id': 'bk-stain-'+currentVal+'-2','name': 'bk-stain-'+currentVal});
    $('#bk-stain-reason-'+nextVal).attr({'id': 'bk-stain-reason-'+currentVal,'name': 'bk-stain-reason-'+currentVal});

   }
   
       
       
        for(var i=0;i<childDiv.length;i++){
           
            var itemId=parseInt(childDiv[i].split('-')[2]);
           var lastElementId=childDiv.length;
            if (itemId>currentVal){
               
                $('#'+childDiv[i]).attr('id', 'bk-item-'+(parseInt(itemId)-1));
                $('#bk-title-'+itemId).attr('id', 'bk-title-'+(parseInt(itemId)-1));
                $('#bk-del-btn-'+itemId).attr('id', 'bk-del-btn-'+(parseInt(itemId)-1));
                $('#bk-del-btn-'+(parseInt(itemId)-1)).show();
                $('#bk-title-'+(parseInt(itemId)-1)).html($(".bk-select").val()+(parseInt(itemId)-1)); /* To change title */
                $('#bk-size-'+itemId).attr({'id': 'bk-size-'+(parseInt(itemId)-1),'name': 'bk-size-'+(parseInt(itemId)-1)});
                $('#bk-age-'+itemId).attr({'id': 'bk-age-'+(parseInt(itemId)-1),'name': 'bk-age-'+(parseInt(itemId)-1)});
                $('#bk-material-'+itemId).attr({'id': 'bk-material-'+(parseInt(itemId)-1),'name': 'bk-material-'+(parseInt(itemId)-1)});
                $('#bk-color-'+itemId).attr({'id': 'bk-color-'+(parseInt(itemId)-1),'name': 'bk-color-'+(parseInt(itemId)-1)});
                $('#bk-stain-'+itemId+'-1').attr({'id': 'bk-stain-'+(parseInt(itemId)-1)+'-1','name': 'bk-stain-'+(parseInt(itemId)-1)});
                $('#bk-stain-'+itemId+'-2').attr({'id': 'bk-stain-'+(parseInt(itemId)-1)+'-2','name': 'bk-stain-'+(parseInt(itemId)-1)});
                $('#bk-stain-reason-'+itemId).attr({'id': 'bk-stain-reason-'+(parseInt(itemId)-1),'name': 'bk-stain-reason-'+(parseInt(itemId)-1)});

            }          
        }
        console.log('itemid is '+itemId);
        if(counter>1){
            counter=parseInt(itemId)-1;
            console.log('counter is '+counter);
            $('#sectioncounter_id').val(counter);
        }
       
       


}
