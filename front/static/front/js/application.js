// my custom validation method

jQuery.validator.addMethod("cleanUrl", function(value, element) {
    return this.optional(element) || /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/i.test(value);
}, jQuery.validator.messages.url);


jQuery.validator.addMethod("username", function(value, element) {
    return this.optional(element) || /^[a-zA-Z0-9_-]{3,255}$/i.test(value);
}, jQuery.validator.messages.username);


$(document).ready(function() {
	
	// timeago
	$('.timeago').timeago();

	// dropdowns
	$('.dropdown-toggle').dropdown();

	// form validation
	$("form").validate({
		errorElement : 'span',
		errorPlacement : function(error, element) {
			$(element).parents(".control-group").addClass("error");
			error.addClass('help-block');
			$(element).after(error);
		}
	});

	// Init tooltips
	$("[data-toggle=tooltip]").tooltip();

	// JS input/textarea placeholder
	$("input, textarea").placeholder();

	// apply required class to required labels
	$('label.control-label:contains("*")').addClass('required');
	
	// hide image urls from django image field
	$('div.controls > input[name*=clear]').each(function(i, obj) {
		var link = $(obj).prev('a');
		if (!link) return;
		link.html('clique aqui');
		link.attr('target', '_blank');
	});

	// add a target='_blank' to every link in markdown
	$('div.markdown a').attr('target', '_blank');

    // help popup for markdown
    $('.markdown_help').on("click", function(e) {
        e.preventDefault();
        bootbox.alert($('.markdown_help_text').html());
    });
});


















