$(document).ready(function() {
  var submitButton = $("#tree-form input[type='submit'");
  var uidInput = $('#tree-form input[name="uid"]');
  var nodes = JSON.parse(document.getElementById('tree').dataset.nodes);

  submitButton.prop('disabled', true);
  $('#tree').fancytree({
    source: nodes,
    activate: function (event, data) {
      if (!data.node.folder) {
        uidInput.attr('value', data.node.key);
        submitButton.prop('disabled', false);
      } else {
        submitButton.prop('disabled', true);
      }
    }
  });

});
