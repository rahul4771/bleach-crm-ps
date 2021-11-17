function ValidateEmail(mail) 
{
    console.log(mail.value,"tre")
 if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail.value) || mail.value == "")
  {
    $('.email_alert').text("");
    return (true)
  }
    // alert("You have entered an invalid email address!")
    $('.email_alert').text("You have entered an invalid email address!")
    return (false)
};

function phonenumber(inputtxt)
{
    phone_id = $(inputtxt).attr('id');
  var phoneno = /^\d{8}$/;

  if((inputtxt.value.match(phoneno)) || (inputtxt.value == ""))
    {
        $('.phone_alert').text("")
        return true;
            }
  else
    {
        $('#'+phone_id+'').siblings('p').text("You have entered an invalid phone number!")
        return false;
            }
}

function mobilenumber(inputtxt)
{
    mobile_id = $(inputtxt).attr('id');
  var mobileno = /^\d{8}$/;
  if((inputtxt.value.match(mobileno)) || (inputtxt.value == ""))
        {
        $('.mobile_alert').text("")
        return true;
        }
      else
        {
        $('#'+mobile_id+'').siblings('p').text("You have entered an invalid mobile number!")
        return false;
        }
}



$(document).ready(function(){
    $('.OnlyNumber').keypress(validateNumber);
    $('.OnlyText').keypress(validateText);});

  function validateNumber(event){  
    //var e = event || window.event;  input[type="number"]
	var charCode = (event.which) ? event.which : event.keyCode
    if (charCode != 46 && charCode > 31 
	&& (charCode < 48 || charCode > 57))
        return false;
        return true;
   }

  function validateText(evt) {
    evt = (evt) ? evt : event;
    var charCode = (evt.charCode) ? evt.charCode : ((evt.keyCode) ? evt.keyCode :
       ((evt.which) ? evt.which : 0));
    if (charCode > 32 && (charCode < 65 || charCode > 90) &&
       (charCode < 97 || charCode > 122)) 
        return false;
        return true;
  }  
  
  
