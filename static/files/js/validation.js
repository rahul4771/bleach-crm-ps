function ValidateEmail(mail) 
{
    console.log(mail)
 if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail))
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
    console.log(inputtxt.value);
  var phoneno = /^\d{8}$/;
  if((inputtxt.value.match(phoneno)))
        {
        $('.mobile_alert').text("")
        return true;
        }
      else
        {
        $('.mobile_alert').text("You have entered an invalid phone number!")
        return false;
        }
}

$(document).ready(function(){
    $('.OnlyNumber').keypress(validateNumber);});
    function validateNumber(event){  
    //var e = event || window.event;  input[type="number"]
	var charCode = (event.which) ? event.which : event.keyCode
    if (charCode != 46 && charCode > 31 
	&& (charCode < 48 || charCode > 57))
        return false;
        return true;
   }