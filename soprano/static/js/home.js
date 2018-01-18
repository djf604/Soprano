function basename(path) {
    return path.replace(/\\/g,'/').replace( /.*\//, '' );
}

$(document).ready(function(){
    $('#sop-home-file').change(function() {
        $('#sop-home-file-display').text(basename($(this).val()));
        $('#sop-home-submit').show(200);
    });

    $('#sop-home-submit').click(function() {
        $('.sop-overlay').css({display: 'flex'});
    });

    $('#sop-home-upload').click(function() {
        $('#sop-start-box').css('display', 'none');
        $('#sop-upload-box').css('display', 'block').addClass('animated fadeInDown');
    });
});
