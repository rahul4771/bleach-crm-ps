
function horzScrollbarDetect() {

  var $scrollable = $('.scrollable');
  var $innerDiv = $('.scrollable > div');

  // Check if elements exist before accessing properties
  if ($innerDiv.length > 0 && $innerDiv.get(0)) {
    if ($innerDiv.outerWidth() < $innerDiv.get(0).scrollWidth) {

      $scrollable.addClass('is-scrollable');
      console.log('Scrollbar, WOOT!');

    } else {

      $scrollable.removeClass('is-scrollable');
      console.log('There is no scrollbar, only Zuul');

    }
  }

}

$(document).ready(function () {

  horzScrollbarDetect();
  console.log('document. boom. ready.');

});

$(window).resize(function () {

  horzScrollbarDetect();
  console.log('window resized');

});