createpptx.operations = function() {
    function process_start(process_css_name,
                           process_class_name,
                           extra_args) {
        if (extra_args == undefined) {
            extra_args = [];
        }
        $('#operation-' + process_css_name).click(function() {
            //var filenames_input = get_filenames_list();
            //var filebrowse_path = $('#id_path').val();
            //var suffix = '/';
            //if (filebrowse_path.charAt(filebrowse_path.length-1)
            //    == '/') {
            //    suffix = '';
            //}
            //filebrowse_path += suffix;
            var args = {
                'extra_args': ''
            };
            for (var i = 0; i < extra_args.length; i++) {
                args['extra_args'] += (args['extra_args'] != '' ? ';'
                                                                : '') +
                                      $('#operation-' +
                                      process_css_name + '-' +
                                      extra_args[i]).val();
            }
            $.getJSON(SCRIPT_ROOT + '/process/start/' +
                      process_class_name + '/',
            args,
            function(data) {
                $('#operation-' + process_css_name).attr('disabled',
                                                         'disabled');
                $('#operation-' + process_css_name + '-progress')
                .progressbar('option', 'disabled', false);
                $('#operation-' + process_css_name + '-progress')
                .progressbar('option', 'value', data.percent);
                setTimeout(function() {
                    process_progress(process_css_name,
                                     process_class_name,
                                     data.key);
                }, 100);
            });
            //alert('createpptx function');
            return false;
        });
    }
    
    function process_progress(process_css_name,
                              process_class_name,
                              key) {
        $.getJSON(SCRIPT_ROOT + '/process/progress/' +
                  process_class_name + '/',
        {
            'key': key
        }, function(data) {
            $('#operation-' + process_css_name + '-progress')
            .progressbar('option', 'value', data.percent);
            if (!data.done) {
                setTimeout(function() {
                    process_progress(process_css_name,
                                     process_class_name,
                                     data.key);
                }, 100);
            }
            else {
                $('#operation-' + process_css_name)
                .removeAttr('disabled');
                $('#operation-' + process_css_name + '-progress')
                .progressbar('option', 'value', 0);
                $('#operation-' + process_css_name + '-progress')
                .progressbar('option', 'disabled', true);
                operation_finished();
            }
        });
    }

    function operation_finished() {
        alert("finished")
    }
    
    return {
        init: function() {
            $('.operation-progress').progressbar({'disabled': true});
            
            /*$('#select-all').click(function() {
                $('.filebrowse-checkbox').attr('checked', 'checked');
                return false;
            });
            $('#select-none').click(function() {
                $('.filebrowse-checkbox').removeAttr('checked');
                return false;
            });
            
            $('#id_path').keyup(function() {
                refresh_photos(true);
                return true;
            });*/
            
            //process_start('reorient', 'ExifTranProcess');

            // cssname, classname
            process_start('createpptx', 'CreatePPTXProcess');
            /*process_start('shiftdate', 'ShiftDateProcess', ['offset']);
            process_start('renamewithid',
                          'RenameWithIdProcess',
                          ['prefix']);
            process_start('datemodified', 'DateModifiedProcess');
            */
        }
    }
}();


$(function() {
    createpptx.operations.init();
});
