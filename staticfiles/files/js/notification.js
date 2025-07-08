/// Common notification


// Notification Types
//     success
//     error
//     warning




$('#thumbnails')
    .append($('<div class="inv-noti-container inv-noti-success"><div class="d-flex"><div class="inv-msg-div">'+msg+'</div><div onclick="closeNotification()"  class="right-pos inv-pointer"><i class="fa fa-times" aria-hidden="true"></i></div></div></div>')
        .hide()
        .fadeIn(2000)
    );

function showNotification(msg,type){
    if(type == 'success'){
        $("body").append($('<div class="inv-noti-container inv-noti-success"><div class="d-flex"><div class="inv-msg-div">'+msg+'</div><div onclick="closeNotification()"  class="right-pos inv-pointer"><i class="fa fa-times" aria-hidden="true"></i></div></div></div>')
        .hide()
        .fadeIn(1000));
    }else if(type == 'error'){
        $("body").append($('<div class="inv-noti-container inv-noti-error"><div class="d-flex"><div class="inv-msg-div">'+msg+'</div><div onclick="closeNotification()"  class="right-pos inv-pointer"><i class="fa fa-times" aria-hidden="true"></i></div></div></div>')
        .hide()
        .fadeIn(1000));


    }else if(type == 'warning'){

        $("body").append($('<div class="inv-noti-container inv-noti-warning"><div class="d-flex"><div class="inv-msg-div">'+msg+'</div><div onclick="closeNotification()"  class="right-pos inv-pointer"><i class="fa fa-times" aria-hidden="true"></i></div></div></div>')
        .hide()
        .fadeIn(1000));


   }
   setTimeout(function(){ $(".inv-noti-container").remove(); }, 2000);
}

function closeNotification(){
    
    $(".inv-noti-container").remove();
}