// csrf settings
// see: https://docs.djangoproject.com/ja/2.0/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// posts tag-addition request
// see: https://qiita.com/juniskw/items/7fa72f91e3dc899a80ae
function add_tag_submit() {
    console.log({
	'url': $('form#add-tag-form').attr('action'),
	'type': 'POST',
	'data': {
	    'tag_title':$('#add-tag-text').val(),
	    'subtitle_id':$('span#subtitle_id').val(),
	},
    });
    alert('ho');
    // $.ajax({
    // 	'url': $('form#add-tag-form').attr('action'),
    // 	'type': 'POST',
    // 	'data': {
    // 	    'tag_title':$('#add-tag-text').val(),
    // 	    'subtitle_id':$('span#subtitle_id').val(),
    // 	},
    // }).then(
    // 	function (response) {
    // 	    // success
    // 	    alert(response.tag_title)
    // 	},
    // 	function () {
    // 	    // failure
    // 	    alert('failed!!!')
    // 	}
    // );
    return false;
}
$(document).ready(function() {
    $('form#add-tag-form').submit(add_tag_submit)
});
