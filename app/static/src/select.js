function display_images() {
    $.ajax({
        url: $SCRIPT_ROOT + '/_return_frames',
        success: function (data) {
            //List all png or jpg or gif file names in the page
            console.log(data);
            $('main').append(img);
            for (x in data) {
                temp = $('<div/>', {
                    'class': 'container',
                    'value': data[x],
                    'text': 'Frame at ' + data[x] / 10 + ' seconds'
                }).on('click', function () {
                    if ($(this).is('.selected')) {
                        $(this).removeClass('selected');
                    } else {
                        $('div').removeClass('selected');
                        $(this).addClass('selected');
                    }
                });
                $('<img/>', {
                    'src': img + data[x] + '.png',
                }).appendTo(temp);
                $('#main').append(temp);
            }
        }
    });
}
function setup() {
    $('body').append('<h1 id="title">Select Beginning Frames</h1>');
    $('body').append('<div id="description">Select the first frame where the video starts -- when you see the book rather then a homescren or some other screen. If you want to be more precise click on the narrow selection to see the frames around the selected one');
    $('<button/>', {
        'text': 'Narrow Selection',
        'id': 'sel_specific'
    }).appendTo('body').on('click', function () {
        if ($('.selected')[0]) {
            console.log($('.selected').attr('value'))
            $.ajax({
                url: $SCRIPT_ROOT + '_split_mid',
                data: {
                    frame: $('.selected').attr('value'),
                    name: $('#filename').html()
                },
                success: function () {
                    setup_specific(0);
                }
            })

        } else {
            alert('no');
        }
    });
    $('<button/>', {
        'text': 'Select End Frame',
        'id': 'next'
    }).appendTo('body').on('click', function () {
        if ($('.selected').length === 1) {
            $('body').append('<div id="init_frame" style="display:none">' + $('.selected').attr('value') + '</div>');
            $(this).attr('id', 'done');
            setup_end();
        } else {
            alert('Select a frame!');
        }
    })
    $('<div id="main"/>').appendTo('body');
    display_images();

}

function setup_end() {
    $('#main').empty();
    $('#title').html('Select Ending Frame')
    $('#description').html('Select the last frame where you see the book.')
    $('#sel_specific').remove();
    $('#done').before(
        $('<button/>', {
            'text': 'Narrow Selection',
            'id': 'sel_specific'
        }).on('click', function () {
            $.ajax({
                url: $SCRIPT_ROOT + '_split_mid',
                data: {
                    frame: $('.selected').attr('value'),
                    name: $('#filename').html()
                },
                success: function () {
                    setup_specific(1);
                }
            })
        })

    )

    $('#done').off('click').on('click', function () {
        if ($('.selected').length === 1) {
            window.location = $SCRIPT_ROOT + '/select_dims?init_frame=' + $('#init_frame').html() +
                '&name=' + $('#filename').html() +
                '&end_frame=' + $('.selected').attr('value');
        } else {
            alert('Please select a frame');
        }
    }).html('Select Dimensions');
    $.ajax({
        url: $SCRIPT_ROOT + '_split_backward',
        data: {
            name: $('#filename').html()
        },
        success: function () {
            display_images();
        }
    })
}

// sets up the page when you're narrowing down the frame you're selecting.
// type determines what the next button does: goes to selecting the end-frame / the next step
// 0 means setup for beginning, 1 means for end.
function setup_specific(type) {
    if (type === 0) {
        $('#main').empty();
        $('#sel_specific').remove();
        display_images();
    }
    if (type === 1) {
        $('#main').empty();
        $('#sel_specific').remove();
        display_images();
    }

}


$(document).ready(function () {
    setup();
});