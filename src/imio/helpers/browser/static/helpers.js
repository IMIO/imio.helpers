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
function callViewAndReload(baseUrl, view_name, params, force_faceted=false, onsuccess=null) {
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
            if (onsuccess) {
                return onsuccess(data);
            } else {
                window.location.href = data;
                }
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
function toggleDetails(id, toggle_parent_active=true, parent_tag=null, load_view=null, base_url=null, toggle_type='slide') {
  tag = $('#' + id);
  if (toggle_type == 'slide') {
    tag.slideToggle(200);
  } else {tag.fadeToggle(200);}
  if (toggle_parent_active) {
    if (!parent_tag) {
      parent_tag = tag.prev()[0];
    }
    parent_tag.classList.toggle("active");
  }
  if (load_view) {
    inner_content_tag = $('div.collapsible-inner-content', tag);
    if (inner_content_tag.length && !inner_content_tag[0].dataset.loaded) {
      loadContent(inner_content_tag[0], load_view, async=true, base_url, event_name="toggle_details_ajax_success");
    }
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

// make jQuery ajax support 'binary' dataType
$.ajaxTransport("+binary", function (options, originalOptions, jqXHR) {
    // check for conditions and support for blob / arraybuffer response type
    if (window.FormData && ((options.dataType && (options.dataType == 'binary')) || (options.data && ((window.ArrayBuffer && options.data instanceof ArrayBuffer) || (window.Blob && options.data instanceof Blob))))) {
        return {
            // create new XMLHttpRequest
            send: function (headers, callback) {
                // setup all variables
                var xhr = new XMLHttpRequest(),
                    url = options.url,
                    type = options.type,
                    async = options.async || true,
                    // blob or arraybuffer. Default is blob
                    dataType = options.responseType || "blob",
                    data = options.data || null,
                    username = options.username || null,
                    password = options.password || null;

                xhr.addEventListener('load', function () {
                    var data = {};
                    data[options.dataType] = xhr.response;
                    // make callback and send data
                    callback(xhr.status, xhr.statusText, data, xhr.getAllResponseHeaders());
                });

                xhr.open(type, url, async, username, password);

                // setup custom headers
                for (var i in headers) {
                    xhr.setRequestHeader(i, headers[i]);
                }

                xhr.responseType = dataType;
                xhr.send(data);
            },
            abort: function () {
                jqXHR.abort();
            }
        };
    }
});

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
      dataType: 'binary',
      processData: 'false',
      responseType: 'arraybuffer',
      cache: false,
      async: false,
      success: function(data, textStatus, request) {
        if (onsuccess) {
          return onsuccess(data, textStatus, request);
          }
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

function submitFormHelperOnsuccessDefault(data, textStatus, request) {
  cancel_button = $('input#form-buttons-cancel');
  // download file if 'content-disposition' header found
  contentType = request.getResponseHeader('content-type');
  if (contentType && contentType.startsWith('application')) {
    data = new Uint8Array(data);
    // to be able to download the blob and set a correct filename
    // we need to add a fictious link (a), click on it then remove it...
    contentType = request.getResponseHeader('content-type');
    fileName = request.getResponseHeader('Content-Disposition').split("filename=")[1];
    var blob = new Blob([data], {type: contentType});
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    cancel_button.click();
  } else {
    // close the overlay
    if (cancel_button) {
      cancel_button.click();
    }
    // reload faceted
    if (has_faceted()) {
      Faceted.URLHandler.hash_changed();
    } else {
        // window.location.reload(); will keep old values of selected checkboxes
        window.location.href = window.location.href;
    }
  }
}

function temp_disable_link(tag) {
    // avoid double clicks
    tag.style = "pointer-events:none;";
    setTimeout(function() {
        tag.style = "";
    }, 2000);
}