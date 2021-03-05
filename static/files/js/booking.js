$(".chosen-select").chosen();
$("#bk-job-booking-btn").hide();
$("#bk-evaluation-btn").hide();
$(".bk-evaluation-form").hide();
$(".bk-job-booking-form").hide();
$(".bk-item-card").hide();
$(".bk-item-form").hide();
$(".bk-image-container").hide();
$("#bk-del-btn-1").hide();


function selectCheck(){
    destroyAll();
    $(".bk-evaluation-form").hide();
    $(".bk-job-booking-form").hide();
    $(".bk-item-card").hide();
    $(".bk-item-form").hide();
    $(".bk-stain").hide();
    $(".bk-image-container").hide();
    deactivateJob();
    deactivateEval();
    $("#bk-evaluation-btn").show();
    var selectedVal=$(".bk-select").val();
    if(selectedVal=='sofa matress cleaning'||selectedVal=='kitchen cleaning'||selectedVal=='carpet cleaning'||selectedVal=='sanitisation'){
        $('#bk-title-1').html(selectedVal+' 1')
        $("#bk-job-booking-btn").show();
       
    }
    else{
        $("#bk-job-booking-btn").hide();
    }
}
function showEvaluation() {
    
    activateEval();
    deactivateJob();
    

};
function showJobBooking() {
    
    activateJob();
    deactivateEval();
    

};
function activateEval(){
    $(".bk-evaluation-form").show();
    $("#bk-evaluation-btn").removeClass("btn-outline-primary");
    $("#bk-evaluation-btn").addClass("btn-primary");
    $(".bk-item-card").hide();
    $(".bk-item-form").hide();
    $(".bk-stain").hide();
    $(".bk-image-container").hide();
}
function deactivateEval(){
    $(".bk-evaluation-form").hide();
    $("#bk-evaluation-btn").addClass("btn-outline-primary");
    $("#bk-evaluation-btn").removeClass("btn-primary");
}
function activateJob(){
    $(".bk-job-booking-form").show();
    $("#bk-job-booking-btn").removeClass("btn-outline-primary");
    $("#bk-job-booking-btn").addClass("btn-primary");
    $(".bk-item-card").show();
    $(".bk-item-form").show();
    $(".bk-stain").show();
    $(".bk-image-container").show();
}
function deactivateJob(){
    $(".bk-job-booking-form").hide();
    $("#bk-job-booking-btn").addClass("btn-outline-primary");
    $("#bk-job-booking-btn").removeClass("btn-primary");
}

function checkStain(elem){
    console.log("parent is "+$(elem).attr('id'));
    let stain_id=$(elem).attr('id').split('-')[2];
    if($(elem).val()=='yes'){
       console.log("id is"+stain_id)
        $("[name='bk-stain-reason-"+stain_id+"'"+"]").parent('.bk-stain-reason').show();
    }
    else{
       /* $("#bk-stain-reason-"+stain_id).parent('.bk-stain-reason').hide();*/
       $("[name='bk-stain-reason-"+stain_id+"'"+"]").parent('.bk-stain-reason').hide();
    }
}
function destroyAll(){
    var formItems = [];
    $("#bk-main-form > div").each((index, elem) => {
             formItems.push(elem.id);
        });
        for(var i=1;i<formItems.length;i++){
            if(formItems[i].length>2 && formItems[i]!='bk-item-1'){
                $('#'+formItems[i]).remove();
            }
            
        }
       counter=1;
        
}


 
