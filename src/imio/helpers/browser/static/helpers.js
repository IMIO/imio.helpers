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

// ajax call managing a call to a given p_view_name and reload taking faceted into account
function callViewAndReload(baseUrl, view_name, params, force_faceted=false) {
  redirect = '0';
  if (!force_faceted && !has_faceted()) {
    redirect = '1';
  }
  $.ajax({
    url: baseUrl + "/" + view_name,
    data: params,
    dataType: 'html',
    cache: false,
    async: true,
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if ((redirect === '0') && !(data)) {
            Faceted.URLHandler.hash_changed();
        }
        else {
            window.location.href = data;
        }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}
