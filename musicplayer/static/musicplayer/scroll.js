$(document).on('scroll', function(){
    if ( $(window).scrollTop() > 30) {
        $('header').addClass('change-color');
    } else {
        $('header').removeClass('change-color');
    }
  });
  
  $(document).on('scroll', function(){
    if ( $(window).scrollTop() > 30) {
        $('.header-logo').addClass('change-logo');
    } else {
        $('.header-logo').removeClass('change-logo');
    }
  });