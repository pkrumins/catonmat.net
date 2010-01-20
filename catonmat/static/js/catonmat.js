/*
** Peteris Krumins (peter@catonmat.net)
** http://www.catonmat.net  --  good coders code, great reuse
**
** The new catonmat.net website.
**
** Code is licensed under GNU GPL license.
*/

catonmat = {

  /* Displays the comment form #comment_form after the element 
  ** 'element' and sets the hidden parent_id field to 'parent_id'.
  */
  show_comment_form: function(element, parent_id) {
    /* Display the comment form after 'element' and slide it out nicely */
    $('#comment_form').
      insertAfter(element).
      hide().
      slideDown('slow');

    /* Set the parent_id form value to the id of the comment we are
    ** replying to. */
    $('#parent_id').val(parent_id);
  },

  /* Restores the reply form to the end of the article (cancels replying). */
  restore_comment_form: function() {
    var p = $('#cancel_comment');
    catonmat.show_comment_form(p, '');
    p.hide();
    $('.comment_reply a.cancel').hide();
  },

  /* Attach event handler to 'Reply to this comment', etc. */
  init_comments: function() {
    $('.comment_reply a').click(
      function(event) {
        var parent_id = this.id.split('_')[2];
        catonmat.show_comment_form($(this).parent(), parent_id);

        /* Hide all existing 'Cancel' buttons */
        $('.comment_reply a.cancel').hide();
        $('#cancel_comment').hide()

        /* Add a paragraph at the end of the comment list with a link to
        ** cancel replying, if the user wants just to add a new comment. */
        var a = $('<a href="#">Click here</a>').click(
                  function(event) {
                    catonmat.restore_comment_form();
                    event.preventDefault();
                  }
                );
        $('<p>').
          attr('id', 'cancel_comment').
          append(a).
          append(' to leave a new comment instead of replying to someone.').
          insertAfter('div.add h3');

        /* Add the 'Cancel' button, which when clicked cancels the comment form,
        ** and restores it back to the end of the article. */
        $('<a href="#" class="cancel">Cancel</a>').
          insertAfter(this).click(
            function(event) {
              catonmat.restore_comment_form();
              event.preventDefault();
          }
        );
        event.preventDefault();
      }
    );
  },

  init_toggle_contacts: function() {
    var img_more = $("<img src=\"/static/img/more-10x10.gif\" class=\"more\">");
    var img_less = $("<img src=\"/static/img/less-10x10.gif\" class=\"more\">");
    $('#a-more-contacts').click(
      function(event) {
        if ($(this).text() === "more") {
          $(this).text("less").prepend(img_less);
        }
        else {
          $(this).text("more").prepend(img_more);
        }
        $('#div-more-contacts').slideToggle('fast');
        event.preventDefault();
      }
    );
  },

  init_why_email: function() {
    $('#why_email_a').click(
      function(event) {
        $('#why_email_explain').slideToggle('fast');
        event.preventDefault();
      }
    );
  },

  init_preview_comment: function() {
    /* TODO: better error checking (network timeout, etc.) */
    $('#preview').click(
      function(event) {
        $('#comment_error').slideUp();
        $.post("/_service/comment_preview",
          $('#comment_form form').serialize(),
          function(data) {
            if (data.status === "error") {
              $('#comment_preview').slideUp();
              $('#comment_error').
              html("<span>" + data.message + "</span>").
              slideDown('fast');
            }
            else {
              $('#comment_preview').
              html(data.comment).
              slideDown('fast');
            }
          },
          "json"
        );
        event.preventDefault();
      }
    );
  }

};

