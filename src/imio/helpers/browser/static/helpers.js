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

// return the canonical url in JS, so the URL of the main object, useful when on a view
function canonical_url() {
  return $("link[rel='canonical']").attr('href');
}

// used to show/hide details
function toggleDetails(id, toggle_parent_active=true, parent_tag=null, load_view=null, base_url=null) {
  tag = $('#' + id);
  tag.slideToggle(200);
  if (toggle_parent_active) {
    if (!parent_tag) {
      parent_tag = tag.prev()[0];
    }
    parent_tag.classList.toggle("active");
  }
  inner_content_tag = $('div.collapsible-inner-content', tag)[0];
  if (load_view && !inner_content_tag.dataset.loaded) {
    loadContent(inner_content_tag, load_view, async=true, base_url, event_name="toggle_details_ajax_success")
  }
}

function loadContent(tag, load_view, async=true, base_url=null, event_name=null) {
    // load content in the collapsible-inner-content div
    var url = base_url || canonical_url();
    url = url + '/' + load_view;
    $.ajax({
      url: url,
      dataType: 'html',
      data: {},
      cache: false,
      async: async,
      success: function(data) {
        tag.innerHTML = data;
        tag.dataset.loaded = true;
        /* trigger event when ajax success, this let's register some JS
         * initialization in returned HTML */
        if (event_name) {
          $.event.trigger({
              type: event_name,
              tag: tag});
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        /*console.log(textStatus);*/
        window.location.href = window.location.href;
        }
    });
}

function setoddeven() {
  var tbody = $(this);
  // jquery :odd and :even are 0 based
  tbody.find('tr').removeClass('odd').removeClass('even')
  .filter(':odd').addClass('even').end()
  .filter(':even').addClass('odd');
}

function submitFormHelper(form, onsuccess=submitFormHelperOnsuccessDefault, onerror=null) {
    $('input#form-buttons-apply').click(function(event) {
      event.preventDefault();
      data = $(this.form).serializeArray();
      // buttons are not included by serializeArray but we need it
      buttons = $("input[name^='form.buttons']", this.form);
      buttons.each(function() {data.push({name: this.name, value: this.value});});
      // include ajax_load meaning we are in an overlay
      data.push({name: "ajax_load", value: true});
      $.ajax( {
      type: 'POST',
      url: this.form.action,
      data: data,
      cache: false,
      async: false,
      success: function(data) {
        if (onsuccess) {return onsuccess(data);}
      },
      error: function(jqXHR, textStatus, errorThrown) {
        if (onerror) {
          return onerror(data);
        }
        else {
          window.location.href = canonical_url();
        }
      },
    } );
  });
}

function submitFormHelperOnsuccessDefault(data) {
  // close the overlay
  cancel_button = $('input#form-buttons-cancel');
  if (cancel_button) {
    cancel_button.click();
  }
  // reload faceted
  if (has_faceted) {
    Faceted.URLHandler.hash_changed();
  }
}
