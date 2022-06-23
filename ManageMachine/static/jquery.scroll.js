$(function() {
  var pagetop = $('#pagetop');
  pagetop.css({'display': 'none'});
  $(window).on('scroll', function() {
  //スクロールが100以上で表示
    if ($(this).scrollTop() > 100) {
      pagetop.fadeIn("slow");
    }
    else {
      pagetop.fadeOut("slow");
    }
  });
    //スクロール
  $('a[href^=#]').click(function() {
    var href = $(this).attr("href");
    var target = $(href == "#" || href == "" ? 'html' : href);
    var position = target.offset().top;
    //500は速度
    $("html, body").animate({scrollTop:position}, 500, 'swing');
        return false;
  });
});
