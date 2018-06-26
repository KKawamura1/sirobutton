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
function failed_in_add_tag_submit(jqXHR, textStatus, errorThrown, response) {
    $('#error-show-button').removeClass('hidden');
    if (typeof response === null) {
	// no http response
	$("#add-tag-error-body").html("<p>通信エラーです。status: " + jqXHR.status + "</p>" + errorThrown);
    } else {
	// response exists
	if (response['status_code'] === 1) {
	    $("#add-tag-error-body").html("<p>そのタグはすでに付けられています。</p>");
	} else if (response['status_code'] === 2) {
	    $("#add-tag-error-body").html("<p>タグの内容がありません。</p>")
	} else {
	    $("#add-tag-error-body").html("<p>サーバー側のエラーです。</p><p>" + response['error_message'] + "</p>");
	}
    }
}
function add_tag_submit() {
    $('#error-show-button').addClass('hidden');
    $('#add-tag-error-collapse').removeClass('show');
    var subtitle_id = $('span#subtitle_id').text();
    $.ajax({
    	'url': $('form#add-tag-form').attr('action'),
    	'type': 'POST',
    	'data': {
    	    'tag_title': $('#add-tag-text').val().replace(/</g, "&lt;").replace(/>/g, "&gt;"),
    	    'subtitle_id': subtitle_id,
    	},
    }).done(function (response, textStatus, jqXHR) {
	var created = response['created'];
	if (created) {
	    // success
	    // make a new tag button
	    var lists_url = $('span#subtitle_lists_url').text();
	    var remove_url = $('span#remove_tag_url').text();
	    var tag_title = response['tag_title'];
	    var tag_id = response['tag_id'];
	    $('span#tags-span').append(
		`
<span id="tag-${ tag_id }" class="each-tag m-1">
 <a class="btn btn-tag btn-sm" role="button" href=${ lists_url }?tag=${ tag_title }>${ tag_title }</a>
 <a class="tag-delete-button" href="#" role="button" onclick="return remove_tag('${ tag_id }', '${ tag_title }', '${ subtitle_id }', '${ remove_url }');">×</a>
</span>
`
	    );
	    $('#add-tag-text').val("");
	} else {
	    // fail
	    failed_in_add_tag_submit(jqXHR, textStatus, null, response);
	}
    }).fail(function (jqXHR, textStatus, errorThrown) {
	failed_in_add_tag_submit(jqXHR, textStatus, errorThrown, null);
    });
    return false;
}
$(document).ready(function() {
    $('form#add-tag-form').submit(add_tag_submit);
});

// posts tag-removing request
function failed_in_remove_tag_submit(jqXHR, textStatus, errorThrown, response) {
    $('#error-show-button').removeClass('hidden');
    if (typeof response === null) {
	// no http response
	$("#add-tag-error-body").html("<p>通信エラーです。status: " + jqXHR.status + "</p>" + errorThrown);
    } else {
	// response exists
	if (response['status_code'] === 1) {
	    $("#add-tag-error-body").html("<p>そのタグはすでに削除されています。</p>");
	} else {
	    $("#add-tag-error-body").html("<p>サーバー側のエラーです。</p><p>" + response['error_message'] + "</p>");
	}
    }
}
function remove_tag_submit(tag_id, subtitle_id, url) {
    $('#error-show-button').addClass('hidden');
    $('#add-tag-error-collapse').removeClass('show');
    $.ajax({
    	'url': url,
    	'type': 'POST',
    	'data': {
    	    'tag_id':tag_id,
    	    'subtitle_id':subtitle_id,
    	},
    }).done(function (response, textStatus, jqXHR) {
	var removed = response['removed'];
	if (removed) {
	    // success
	    tag_title = response['tag_title']
	    $(`span#tag-${tag_id}`).remove();
	    $('#add-tag-text').val(tag_title);
	} else {
	    // fail
	    failed_in_remove_tag_submit(jqXHR, textStatus, null, response);
	}
    }).fail(function (jqXHR, textStatus, errorThrown) {
	failed_in_remove_tag_submit(jqXHR, textStatus, errorThrown, null);
    });
    return false;
}
function remove_tag(tag_id, tag_title, subtitle_id, url) {
    var okay = window.confirm(`タグ ${ tag_title } を削除してもよろしいですか？`);
    if (okay) {
	remove_tag_submit(tag_id, subtitle_id, url);
    }
    return false;
}
