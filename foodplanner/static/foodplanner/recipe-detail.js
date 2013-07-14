$(function () {
    /*
     * Autocompletion for the ingredient form.
     */
    function setup_portionsize_select (values) {
        var selectbox = $("#select-portionsize");
        selectbox.children().remove();
        for (var i in values) {
            selectbox.append('<option value="' + values[i].pk + '">' +
                             values[i].label + '</option>');
        }
        selectbox.removeAttr('disabled');
    }

    $("#ingredient-input").autocomplete({
        source: "/ingredient/ajax/",
        minLength: 2,
        select: function (event, ui) {
            if (ui.item) {
                $("#select-portionsize").attr('disabled', 'disabled');
                $.getJSON("/ingredient/portionsize/ajax/?ingredient=" +
                          ui.item.value,
                          setup_portionsize_select);
            }
        }
    });

    /*
     * Make the ingredient list sortable.
     */
    $("#sortable").sortable({
        handle: ".move-button",
        update: function(event, ui) {
            var neworder = [];
            $(this).children().each(function () {
                neworder.push($(this).data('portionpk'));
            });
            $.post("/portion/reorder/",
                   {'csrfmiddlewaretoken': $(this).data('csrf-token'),
                    'neworder': JSON.stringify(neworder)});
        }
    });
    $(".move-button").css("cursor", "move");
});
