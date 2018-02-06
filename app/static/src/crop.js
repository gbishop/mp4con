$(document).ready(function () {
    var jcrop_api;
    var counter = 0;
    // Ensures active is false and not null, tsel and psel set to selection objects later
    var tsel = { active: false };
    var psel = { active: false };
    var options = {
        multi: true,
        multiMax: 2,
    }

    $('#target').Jcrop(options, function () {
        jcrop_api = this;
        init_interface();
    });

    $('#interface').on('cropmove cropend', function (e, s, c) {
        if (tsel.active) {
            $('#text_inf #tcropx').val(c.x);
            $('#text_inf #tcropy').val(c.y);
            $('#text_inf #tcropw').val(c.w);
            $('#text_inf #tcroph').val(c.h);
        }
        if (psel.active) {
            $('#pic_inf #pcropx').val(c.x);
            $('#pic_inf #pcropy').val(c.y);
            $('#pic_inf #pcropw').val(c.w);
            $('#pic_inf #pcroph').val(c.h);
        }
    });


    function init_interface() {
        tsel = jcrop_api.newSelection().update(
            $.Jcrop.wrapFromXywh([textdims.xmin, textdims.ymin, textdims.xmax - textdims.xmin, textdims.ymax - textdims.ymin])
        );

        // Just a small hacky thing, prevents the coordinates of tsel from being changed
        // with the creation of psel
        tsel.active = false;

        psel = jcrop_api.newSelection().update(
            $.Jcrop.wrapFromXywh([picdims.xmin, picdims.ymin, picdims.xmax - picdims.xmin, picdims.ymax - picdims.ymin])
        );
    }



    $('#submit').on('click', function () {
        if ($('#email').val()) {

            $.ajax({
                url: $SCRIPT_ROOT + '/process',
                data: {
                    tcropx: $('#tcropx').attr('value'),
                    tcropy: $('#tcropy').attr('value'),
                    tcropw: $('#tcropw').attr('value'),
                    tcroph: $('#tcroph').attr('value'),
                    pcropx: $('#pcropx').attr('value'),
                    pcropy: $('#pcropy').attr('value'),
                    pcropw: $('#pcropw').attr('value'),
                    pcroph: $('#pcroph').attr('value'),
                    init: $('#init').html(),
                    end: $('#end').html(),
                    name: $('#filename').attr('value'),
                    email: $('#email').val(),
                    folder: $('#folder').attr('value'),
                    parent: $('#parent').attr('value')
                }
            })
            window.location = $SCRIPT_ROOT + '/';
        } else {
            alert('Enter in an email!')
        }
    })

});
