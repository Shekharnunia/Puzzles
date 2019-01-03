$(function () {
    $(".publish").click(function () {
        $("input[name='status']").val("P");
        $("#article-form").submit();
    });

    $(".update").click(function () {
        $("input[name='status']").val("P");
        //$("input[name='edited']").prop("checked");
        $("input[name='edited']").val("True");
        $("#article-form").submit();
    });

    $(".draft").click(function () {
        $("input[name='status']").val("D");
        $("#article-form").submit();
    });
});


  $("#comment").focus(function () {
    $(this).attr("rows", "3");
    $("#comment-helper").fadeIn();
  });

  $("#comment").blur(function () {
    $(this).attr("rows", "1");
    $("#comment-helper").fadeOut();
  });

  $("#comment").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      $.ajax({
        url: '/articles/comment/',
        data: $("#comment-form").serialize(),
        cache: false,
        type: 'post',
        success: function (data) {
          $("#comment-list").html(data);
          var comment_count = $("#comment-list .comment").length;
          $(".comment-count").text(comment_count);
          $("#comment").val("");
          $("#comment").blur();
        }
      });
    }
  });

});
