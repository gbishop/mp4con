// folder = absolute path to the temp folder containing the video.
//      This is in the get call for _split as cv2 needs the absolute path
//      TODO ask if this might be a security risk??
//  rel_folder = relative path to the temp folder, this is to just make stuff easier down the road...
//  folder0 = relative static path to folder containing the initial split frames.
//      THIS CHANGES IF YOU SELECT NARROW SEL FOR THE FIRST ONE IN ORDER TO DISPLAY IT IN 
//      THE SELECTION!
//  filename = name of the video



function display_images(folder) {
    $.ajax({
        url: $SCRIPT_ROOT + '/_return_frames',
        data: { "folder": folder },
        success: function (data) {
            //List all png or jpg or gif file names in the page
            // $('main').append(img_folder0);
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
                    'src': folder + "/" + data[x] + '.png',
                }).appendTo(temp);
                $('#main').append(temp);
            }
        }
    });
}
function setup() {
    $('body').append('<div id="box"></div>');
    $('#box').append('<div id="header"></div>')
    $('#header').append('<h1 id="title">Select Beginning Frames</h1>');
    $('#header').append('<div id="description">Select the first frame where the video starts -- when you see'+
        'the book rather then a homescren or some other screen. If you want to be more precise click on the narrow selection to'+
        'see the frames around the selected one. You should only narrow selection if the image at 0 seconds doesn\'t show the book.'+
        'If you see any "broken" images, those are not a problem, they are just a product of the program trying to show frames past the length of the video');
    $('<button/>', {
        'text': 'Narrow Selection',
        'id': 'sel_specific'
    }).appendTo('#header').on('click', function () {
        if ($('.selected')[0]) {
            console.log($('.selected').attr('value'))
            $.ajax({
                url: $SCRIPT_ROOT + '_split_mid',
                data: {
                    init: $('.selected').attr('value'),
                    root: folder,
                    file: filename
                },
                success: function (path) {
                    folder0=path;
                    setup_specific(path);
                }
            })

        } else {
            alert('Select a Frame');
        }
    });
    $('<button/>', {
        'text': 'Select End Frame',
        'id': 'next'
    }).appendTo('#header').on('click', function () {
        if ($('.selected').length === 1) {
            $('body').append('<div id="init_frame" style="display:none">' + $('.selected').attr('value') + '</div>');
            $(this).attr('id', 'done');
            setup_end();
        } else {
            alert('Select a frame!');
        }
    })
    $('<div id="main"/>').appendTo('#box');
    display_images(folder0);

}

function setup_end() {
    $('#main').empty();
    $('#title').html('Select Ending Frame')
    $('#description').html('Select the last frame where you see the book. Ignore any broken frames at the end. At this stage you usually want to select narrow selection then pick the last frame where you see the book.')
    $('#sel_specific').remove();
    $('#done').before(
        $('<button/>', {
            'text': 'Narrow Selection',
            'id': 'sel_specific'
        }).on('click', function () {
            $.ajax({
                url: $SCRIPT_ROOT + '_split_mid',
                data: {
                    init: $('.selected').attr('value'),
                    root: folder,
                    file: filename
                },
                success: function (path) {
                    setup_specific(path);
                }
            })
        })

    )

    $('#done').off('click').on('click', function () {
        if ($('.selected').length === 1) {
            window.location = $SCRIPT_ROOT + '/select_dims?init_frame=' + $('#init_frame').html() +
                '&name=' + filename +
                '&end_frame=' + $('.selected').attr('value') +
                '&folder='+folder0+
                '&parent='+rel_folder;
        } else {
            alert('Please select a frame');
        }
    }).html('Select Dimensions');
    $.ajax({
        url: $SCRIPT_ROOT + '_split_end',
        data: {
            file: filename,
            root: folder
        },
        success: function (path) {
            display_images(path);
        }
    })
}

// sets up the page when you're narrowing down the frame you're selecting.
// type determines what the next button does: goes to selecting the end-frame / the next step
// 0 means setup for beginning, 1 means for end.
//
// I'm honestly not sure why I wrote this?? I'll change it later
function setup_specific(path) {
    $('#main').empty();
    $('#sel_specific').remove();
    display_images(path);


}


$(document).ready(function () {
    setup();
});
