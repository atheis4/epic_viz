'use strict';


$(function() {
  var $resultDiv = $('div#results');

  $resultDiv.on('mousemove', 'div.me-tile', function(e) {
    var meId = $(this).attr('data-me-id');
    var metadata = $('div#' + meId);
    metadata.css(
      {'display': 'block',
       'top': e.pageY - 150,
       'left': e.pageX});
  });

  $resultDiv.on('mouseout', 'div.me-tile', function() {
    var metadataTiles = $('div.metadata');
    metadataTiles.css('display', 'none');
  });
});
