$(document).ready(function() {

	function slugify(name) {
		if(!name){
			return "";
		}

		return name.replace(' ','-').replace('*','-').replace('+','-').replace('.','-')
	}

	$('.btn-share-file').on('click',function(){
		const $this = $(this);

		var myModal = new bootstrap.Modal(document.getElementById('shareModal'));
		myModal.show();
		console.log("Modal is now shown");


		const fileId = $this.attr('data-file-id');
		console.log("FileID is " + fileId)

		const fileName = $this.attr('data-file-name');
		const fileNameSlugified = slugify(fileName);

		const permalink = 'http://localhost:5000' + '/download/' + fileId + '/' + fileNameSlugified;
		console.log("permalink is " + permalink)

		$('#shareModal .share-link').html(permalink) 


	});


	// File upload drap and drop UI

	var options = {iframe: {url: '/handle_file_upload'}};
	var zone = new FileDrop('zbasic', options);

	zone.event('send', function (files) {
	  files.each(function (file) {
	    file.event('done', function (xhr) {
	      alert('Done uploading ' + this.name + ',' +
	            ' response:\n\n' + xhr.responseText);
	    });

	    file.event('error', function (e, xhr) {
	      alert('Error uploading ' + this.name + ': ' +
	            xhr.status + ', ' + xhr.statusText);
	    });

	    file.sendTo('handle_file_upload');
	  });
	});

	// <iframe> uploads are special - handle them.
	zone.event('iframeDone', function (xhr) {
	  alert('Done uploading via <iframe>, response:\n\n' + xhr.responseText);
	});

	// Toggle multiple file selection in the File Open dialog.
	fd.addEvent(fd.byID('zbasicm'), 'change', function (e) {
	  zone.multiple((e.currentTarget || e.srcElement).checked);
	});

});

