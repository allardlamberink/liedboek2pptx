function allardtest(arg) {
	alert(arg);
}


function PPTXsummary() {
	var songorder="";
	$('.sortable li').each(function(i) {
	if (songorder=='')
		songorder = $(this).attr('id');
	else
		songorder += "," + $(this).attr('id');
	});

	var lied_element = document.getElementById("liedvolgorde");
	lied_element.value = songorder;
	lied_element.form.submit();
}
