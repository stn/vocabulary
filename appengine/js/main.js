$('#wordModal').on('show.bs.modal', function (e) {
    var link = $(e.relatedTarget);
    $('#wordModalBody').load(link.attr('href'));
});

$('#saveWord').on('click', function (e) {
    e.preventDefault();
    var form = $('#wordForm');
    $.ajax({
        url: form.attr('action'),
        type: form.attr('method'),
        data: form.serialize(),
        success: function () {
            $('#wordModal').modal('hide');
        },
    });
});

$('#deleteWord').on('click', function (e) {
    e.preventDefault();
    var form = $('#wordForm');
    $.ajax({
        url: '/delete_word',
        type: form.attr('method'),
        data: form.serialize(),
        success: function () {
            $('#wordModal').modal('hide');
        },
    });
});
