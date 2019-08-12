var sum;
var tries;
emailValidator = /^[\w._-]+[+]?[\w._-]+@[\w.-]+\.[a-zA-Z]{2,6}$/;

$(document).on('input propertychange keyup', "textarea[name='message']", function () {
	checkForm('');
});

// ====================== FOR TABS TO WORK ==========================================
$('#tabsul a').click(function(e) {
	e.preventDefault();
$(this).tab('show');
});

// store the currently selected tab in the hash value
$("ul.nav-tabs > li > a").on("shown.bs.tab", function(e) {
	var id = $(e.target).attr("href").substr(1);
	window.location.hash = id;
});

// on load of the page: switch to the currently selected tab
var hash = window.location.hash;
$('#tabsul a[href="' + hash + '"]').tab('show');

// =================================================================================

function writeEmail() {
	emailE='gmail.com';
	emailI='ieee.org';
	emailE=('cdalamagkas' + '@' + emailE + '<br/>' + 'cdalamagkas' + '@' + emailI);
	
	document.getElementById("email-js").innerHTML = emailE;
}

function clearError(string){
	document.getElementById(string + "-div").classList.remove('has-error'); 
	document.getElementById(string + "-div").classList.remove('has-feedback');
	document.getElementById(string + "-span").classList.remove('glyphicon'); 
	document.getElementById(string + "-span").classList.remove('glyphicon-remove');
	document.getElementById(string + "-span").classList.remove('form-control-feedback');
}

function clearSuccess(string){
	document.getElementById(string + "-div").classList.remove('has-success');
	document.getElementById(string + "-div").classList.remove('has-feedback');
	document.getElementById(string + "-span").classList.remove('glyphicon');
	document.getElementById(string + "-span").classList.remove('glyphicon-ok');
	document.getElementById(string + "-span").classList.remove('form-control-feedback');
}

function setSuccess(string){
	document.getElementById(string + "-div").classList.add('has-success');
	document.getElementById(string + "-div").classList.add('has-feedback');
	document.getElementById(string + "-span").classList.add('glyphicon');
	document.getElementById(string + "-span").classList.add('glyphicon-ok');
	document.getElementById(string + "-span").classList.add('form-control-feedback');
}

function setError(string){
	document.getElementById(string + "-div").classList.add('has-error');
	document.getElementById(string + "-div").classList.add('has-feedback');
	document.getElementById(string + "-span").classList.add('glyphicon');
	document.getElementById(string + "-span").classList.add('glyphicon-remove');
	document.getElementById(string + "-span").classList.add('form-control-feedback');
}

function disableSubmit(){
	submit = document.getElementById("submit");
	submit.disabled = true;
}

function enableSubmit(){
	submit = document.getElementById("submit");
	submit.disabled = false;
}

function checkEmail(){
	email = document.getElementById("email").value;
	if(email.match(emailValidator)) {
		clearError("email");
		setSuccess("email");
		return true;
	}
	else {
		clearSuccess("email");
		setError("email");
		return false;
	}
}

function checkCaptcha(){
	if (sum == document.getElementById("captcha").value) {
		clearError("captcha");
		setSuccess("captcha");
		enableSubmit();
		return true;
	}
	else {
		clearSuccess("captcha");
		setError("captcha");
		disableSubmit();
		return false;
	}
}

function resetForm(){
	setCaptcha();
	document.getElementById("contactForm").reset();
	disableSubmit();
	clearError("email");
	clearSuccess("email");
}
	
function setCaptcha(){
	document.getElementById("captcha").value = '';
	clearError("captcha");
	clearSuccess("captcha");
	
	a = Math.floor(Math.random()*9)+1;
	b = Math.floor(Math.random()*9)+1;
	sum = a + b;
	document.getElementById("captcha").placeholder = a + " + " + b + " = ?";
}

function checkForm() {
	if (name==null || name=="" || email==null || email=="" || message==null || message=="" || !checkEmail() || !checkCaptcha() )
		return false;
	else
		return true;
}

function sendMessage() {
	name = document.getElementById("name").value;
	email = document.getElementById("email").value;
	subject = document.getElementById("subject").value;
	message = document.getElementById("message").value;
	
	if (checkForm()) {
		swal({
			title: 'Are you sure?',
			text: "Please press the confirm button if you indeed want to send your message.",
			type: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Confirm'
		}).then(function () {
			$.ajax({
				url : './contact_me.php',
				type : 'POST',
				data : {
					name : name,
					email: email,
					subject : subject,
					message : message
				},
				success : function(data, textStatus, XMLHttpRequest)
				{
					var response = $.parseJSON(data);
					console.log(response.success);
					if (response.success) {
						resetForm();
						console.log("got here");
						swal(
							'Success!',
							'Your message has been sent.',
							'success'
						);
					} else {
						swal(
							'Failure...',
							'It seems that my server encountered an error. Please try again later.',
							'error'
						);
					}
				},
				error : function(data, textStatus, XMLHttpRequest)
				{
					swal(
						'Failure...',
						'It seems that my server encountered an error. Please try again later.',
						'error'
					);
				},
			});
		});
	} else {
		swal(
			'Attention',
			'You must fill correctly all required fields marked by <span class="red">*</span>',
			'warning'
		);	
	}
}
