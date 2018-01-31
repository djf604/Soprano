function basename(path) {
    return path.replace(/\\/g,'/').replace( /.*\//, '' );
}

$(function($){
    $('input[type="file"]').first().change(function() {
        $('span.sop-filename-display').first().text(basename($(this).val()));
        $('button[type="submit"]').first().show(200);
    });
    $('button[type="submit"]').first().click(function() {
        $('.sop-overlay').css({display: 'flex'});
    });
});
