$(function () {
    function setup_portionsize_select (values) {
        var selectbox = $("#select-portionsize");
        selectbox.children().remove();
        for (i in values) {
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
        },
    });


    $("#sortable").sortable({
        update: function(event, ui) {
            var neworder = []
            $(this).children().each(function () {
                neworder.push($(this).data('portionpk'))
            });
            $.post("/portion/reorder/",
                   {'csrfmiddlewaretoken': $(this).data('csrf-token'),
                    'neworder': JSON.stringify(neworder)});
        }
    });
    $("#sortable").disableSelection();
    $("#sortable").css("cursor", "move");
});
