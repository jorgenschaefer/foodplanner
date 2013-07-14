$(function () {
    /*
     * Add input editing.
     */
    $(".click-to-edit").dblclick(function () {
        var element = $(this),
            url = $(this).data("url"),
            csrf = $(this).data("csrf"),
            value = $(this).text();

        var input = $('<input type="number" class="input-mini" ' +
                      'name="value" value="' + value + '">\n'),
            form = $('<form style="display: inline" method="post"'
                     + ' action="' + url + '">\n' +
                     '<input type="hidden" ' +
                     '       name="csrfmiddlewaretoken" ' +
                     '       value="' + csrf + '" />' +
                     '</form>');
        input.blur(function () {
            element.html(value);
        });
        form.append(input);
        form.submit(function () {
            value = input.val();
            return true;
        });
        $(this).html(form);
        input.select();
    });
});
