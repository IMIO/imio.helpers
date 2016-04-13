$(document).ready(function(){
  var nodes = JSON.parse(document.getElementById('tree').dataset.nodes);
  $('#tree').fancytree({
    source: nodes,
    activate: function (event, data) {
      if (!data.node.folder) {
        $('input[name="uid"]').attr('value', data.node.key);
      }
    }
  });
});
