var smallBreak = 800; // Your small screen breakpoint in pixels
var columns = $('.dataTable tr').length;
var rows = $('.dataTable th').length;

$(document).ready(shapeTable());
$(window).resize(function () {
  shapeTable();
});

function shapeTable() {
  if ($(window).width() < smallBreak) {
    for (i = 0; i < rows; i++) {if (window.CP.shouldStopExecution(0)) break;
      var maxHeight = $('.dataTable th:nth-child(' + i + ')').outerHeight();
      for (j = 0; j < columns; j++) {if (window.CP.shouldStopExecution(1)) break;
        if ($('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').outerHeight() > maxHeight) {
          maxHeight = $('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').outerHeight();
        }
        if ($('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').prop('scrollHeight') > $('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').outerHeight()) {
          maxHeight = $('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').prop('scrollHeight');
        }
      }window.CP.exitedLoop(1);
      for (j = 0; j < columns; j++) {if (window.CP.shouldStopExecution(2)) break;
        $('.dataTable tr:nth-child(' + j + ') td:nth-child(' + i + ')').css('height', maxHeight);
        $('.dataTable th:nth-child(' + i + ')').css('height', maxHeight);
      }window.CP.exitedLoop(2);
    }window.CP.exitedLoop(0);
  } else {
    $('.dataTable td, .dataTable th').removeAttr('style');
  }
}