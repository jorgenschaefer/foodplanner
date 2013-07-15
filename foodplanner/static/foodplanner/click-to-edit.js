$(function () {
    /*
     * Add input editing.
     */
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) ==
                origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) ==
             sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute
            // i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $(".click-to-edit").dblclick(function () {
        var element = $(this),
            url = $(this).data("url"),
            attribute = $(this).data("attribute"),
            csrf_token = $(this).data("csrf"),
            value = $(this).text();

        var input = $('<input type="number" class="input-mini" ' +
                      'name="value" value="' + value + '">\n');
        input.blur(function () {
            element.html(value);
        }).keydown(function (event) {
            if (event.which == 13) {
                element.html('<img'
                             + ' src="/static/foodplanner/spinner.gif"'
                             + ' alt="" />');
                var data = {};
                data[attribute] = input.val();
                $.ajax({
                    url: url,
                    type: "PUT",
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                    beforeSend: function (xhr, settings) {
                        if (!safeMethod(settings.type) &&
                            sameOrigin(settings.url))
                        {
                            xhr.setRequestHeader("X-CSRFToken", csrf_token);
                        }
                    },
                    success: function (data) {
                        element.html(data[attribute]);
                    },
                    error: function () {
                        element.html(value);
                    }
                });
                return false;
            } else {
                return true;
            }
        });
        element.html(input);
        input.select();
    });
});
