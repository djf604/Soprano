$(function($) {
    $('button.filter').click(function() {
        var oldFilterType = $('#filter-type').val();
        var newFilterType = $(this).text().split(' ').map(function(e){return e.toLowerCase()}).join('-');

        if (oldFilterType === newFilterType) return false;

        $('div#' + oldFilterType).slideUp(200, function() {
            $('div#' + newFilterType).slideDown(200);
            $('#filter-type').val(newFilterType);
            if (newFilterType === 'get-all') {$('form').submit()}
        });
    });

    $('form').submit(function() {
        $('.sop-overlay').css({display: 'flex'});
        $.post($(this).attr('action'), $(this).serialize(), function(data, textStatus, response) {
            download(data, response.getResponseHeader('X-Filename'), 'text/csv');
            $('.sop-overlay').css({display: 'none'});
        });
        return false;
    });
});