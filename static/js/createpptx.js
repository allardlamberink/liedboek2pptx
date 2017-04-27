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
                'voorganger': 'allard'
            };
            for (var i = 0; i < extra_args.length; i++) {
                args['extra_args'] += (args['extra_args'] != '' ? ';'
                                                                : '') +
                                      $('#operation-' +
                                      process_css_name + '-' +
                                      extra_args[i]).val();
            }
            $('.operation-progress').show();
            $('.operation-finished').hide();
            $('#operation-' + process_css_name).attr('disabled', 'disabled');
            $('#operation-' + process_css_name + '-progress').progressbar('option', 'disabled', false);
            $.getJSON(SCRIPT_ROOT + '/process/start/' + process_class_name + '/', args,
                function(data) {
                    $('#operation-' + process_css_name + '-progress').progressbar('option', 'value', data.percent);
                    process_progress(process_css_name, process_class_name, data.key);
            });
            return false;
        console.log('klaar met click');
        });
    }



    function process_progress(process_css_name,
                              process_class_name,
                              key) {
            base_url = SCRIPT_ROOT + '/process/progress/' + process_class_name + '/';
            $.getJSON(base_url,
            {
                'key': key,
                _: new Date().getTime()
            }, function( data ) {
                $('#operation-' + process_css_name + '-progress').progressbar('option', 'value', data.percent);
                if (!data.done) {
                    setTimeout(function() {
                        process_progress(process_css_name, process_class_name, data.key);
                    }, 100);
                }
                else {
                    $('#operation-' + process_css_name).removeAttr('disabled');
                    $('#operation-' + process_css_name + '-progress').progressbar('option', 'value', 0);
                    $('#operation-' + process_css_name + '-progress').progressbar('option', 'disabled', true);
                    operation_finished(key);
                }
                
            });
    }


    function operation_finished(file_uuid) {
        $('.operation-progress').hide();
        $('.operation-finished').show();
        $('#file_uuid').val(file_uuid);
    }
    
    return {
        init: function() {
            $('.operation-progress').progressbar({'disabled': true});
            $('.operation-progress').hide();
            $('.operation-finished').hide();
            
            process_start('createpptx', 'CreatePPTXProcess');
        }
    }
}();


$(function() {
    createpptx.operations.init();
});
