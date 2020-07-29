jQuery(function ($) {
  $.fn.dashboard = function (args) {
    var defaults = {
      width: 768,
      sidebar: {
        collapsedClass: 'sidebar-collapsed',
        fixedClass: 'sidebar-fixed',
        beforeCollapse: function () {},
        afterCollapse: function () {} } };


    var settings = $.extend(true, defaults, args);

    init();

    function init() {
      $('[data-toggle-sidebar]').click(function (e) {
        e.preventDefault();
        toggleSidebar();
      });

      $('[data-toggle-fixed]').click(function (e) {
        e.preventDefault();
        toggleFixed();
      });

      $(window).bind("load resize", function () {
        width = window.innerWidth;

        if (width < settings.width)
        collapseSidebar();
      });
    };

    function toggleSidebar() {
      if ($('body').hasClass(settings.sidebar.collapsedClass)) {
        expandSidebar();
      } else {
        collapseSidebar();
      }
    }

    function collapseSidebar() {
      settings.sidebar.beforeCollapse();
      $('body').addClass(settings.sidebar.collapsedClass);
      settings.sidebar.afterCollapse();
    }

    function expandSidebar() {
      $('body').removeClass(settings.sidebar.collapsedClass);
    }

    function toggleFixed() {
      $('body').toggleClass(settings.sidebar.fixedClass);
    }
  };
});

jQuery(function ($) {
  var args = {
    sidebar: {
      beforeCollapse: function () {
        $('.main-sidebar .collapse').collapse('hide');
      } } };


  $('body').dashboard(args);
});
//# sourceURL=pen.js