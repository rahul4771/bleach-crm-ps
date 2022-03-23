$('.lv-dropdown').click(function () {
   
    $(this).attr('tabindex', 1).focus();
    $(this).toggleClass('active');
    $(this).find('.lv-dropdown-menu').slideToggle(300);
});
$('.lv-dropdown').focusout(function () {
    $(this).removeClass('active');
    $(this).find('.lv-dropdown-menu').slideUp(300);
});
$('.lv-dropdown .lv-dropdown-menu li').click(function () {
    console.log("logo")
    $(this).parents('.lv-dropdown').find('span').text($(this).text());
    $(this).parents('.lv-dropdown').find('input').attr('value', $(this).attr('id'));
});
/*End Dropdown Menu*/


$('.lv-dropdown-menu li').click(function () {
    console.log("logo")
var input = '<strong>' + $(this).parents('.lv-dropdown').find('input').val() + '</strong>',
  msg = '<span class="msg">Hidden input value: ';
$('.msg').html(msg + input + '</span>');
}); 

