// fix for Firefox bug that is not able to print a fieldset on several pages, see https://bugzilla.mozilla.org/show_bug.cgi?id=471015
//   we replace <fieldset> by <div class="fieldset"> for the printing process.  Grabbed from https://stackoverflow.com/a/14237116

$(window).bind('beforeprint', function(){
    $('fieldset').each(
        function(item)
        {
            $(this).replaceWith($('<div class="fieldset">' + this.innerHTML + '</div>'));
        }
    );
});
$(window).bind('afterprint', function(){
    $('div.fieldset').each(
        function(item)
        {
            $(this).replaceWith($('<fieldset>' + this.innerHTML + '</fieldset>'));
        }
    );
});

// currently displaying a faceted navigation?
function has_faceted() {
  return Boolean($("div#faceted-form").length);
}
