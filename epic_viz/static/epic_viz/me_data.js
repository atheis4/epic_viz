'use strict';

function clearPageEls() {
  // Remove all elements from the result div
  var $resultDiv = $('div#results');
  var $returnData = $resultDiv.children();
  $returnData.remove();
}


function createMETile(meId, meName, status) {
  // Create the modelable entity tile
  var meTile = $('<div data-me-id="' + meId + '" class="me-tile ' + status + '"></div>');
  var meidEl = $('<h4>Modelable Entity: ' + meId + '</h4>');
  var meNameEl = $('<h4>' + meName + '</h4>');

  meTile.append(meidEl);
  meTile.append(meNameEl);

  return meTile;
}


function createMetadataTile(meId, meType, modelType, mvid, date, description) {
  // Create the metadata tile
  var metadataTile = $('<div id="' + meId + '" class="metadata"></div>');
  var meTypeEl = $('<p><b>Modelable Entity Type:</b> ' + meType + '</p>');
  var modelTypeEl = $('<p><b>Model Type:</b> ' + modelType + '</p>');
  var mvidEl = $('<p><b>Model Version ID:</b> ' + mvid + '</p>');
  var dateEl = $('<p><b>Date Inserted:</b><br>' + date + '</p>');
  var descEl = $('<p><b>Description:</b><br>' + description + '</p>');

  metadataTile.append(meTypeEl);
  metadataTile.append(modelTypeEl);
  metadataTile.append(mvidEl);
  metadataTile.append(dateEl);
  metadataTile.append(descEl);

  return metadataTile;
}


function createME(model) {
  var indModelEl = $('<div class="ind-model"></div>');

  var meId = model.me_id;
  var meName = model.me_name;
  var status = model.status;

  var meTile = createMETile(meId, meName, status);
  indModelEl.append(meTile);
  return indModelEl;
}

function createMetadata(model) {
  var meId = model.me_id;
  var meType = model.me_type;
  var modelType = model.model_type;
  var mvid = model.mvid;
  var date = model.date;
  var description = model.description;

  var metadataTile = createMetadataTile(meId, meType, modelType, mvid, date,
                                        description);
  return metadataTile;
}


function addMeToDiv(mes) {
  var resultDiv = $('div#results');
  var metadataDiv = $('div#metadata');
  var modelDiv = $('<div class="models"></div>');

  for (var i = 0; i < mes.length; i++) {
    var meEl = createME(mes[i]);
    var metadataTile = createMetadata(mes[i]);
    modelDiv.append(meEl);
    metadataDiv.append(metadataTile);
  }

  resultDiv.append(modelDiv);
}


function createTagDateDiv(tag, gbdProcess, date) {
  var tagName = tag.tag_name;
  var gbdProcess = gbdProcess.process;
  var date = date.date;

  var resultDiv = $('div#results');

  var dateDiv = $('<div class="gbd-date"></div>');
  var metadataDiv = $('<div id="metadata"></div>');
  var causeEl = $('<h3>Cause Name: ' + tagName + '</h3>');
  var dateEl = $('<h4>Compared to ' + gbdProcess + ' on ' + date + '</h4>');

  dateDiv.append(causeEl);
  dateDiv.append(dateEl);
  resultDiv.append(dateDiv);
  resultDiv.append(metadataDiv);
}


function noModelResults() {
  var noMeId = 'N/A';
  var noMeName = 'No Modelable Entity for this cause';
  var noStatus = 'gray';

  var meTile = createMETile(noMeId, noMeName, noStatus);

  var resultDiv = $('div#results');
  var modelDiv = $('<div class="models"></div>');
  var indModelEl = $('<div class="ind-model"></div>');

  indModelEl.append(meTile);
  modelDiv.append(indModelEl);
  resultDiv.append(modelDiv);
}


function parseJSONData(data) {
  var tag, gbdProcess, compareDate, models;
  tag = data.tag;
  gbdProcess = data.process;
  compareDate = data.date;
  models = data.models;
  return [tag, gbdProcess, compareDate, models];
}


function createPageEls(data) {
  data = parseJSONData(data);
  var tag = data[0];
  var gbdProcess = data[1]
  var compareDate = data[2];
  var models = data[3];

  createTagDateDiv(tag, gbdProcess, compareDate);

  if (models.length > 0) {
    addMeToDiv(models);
  } else {
    noModelResults();
  }
}


// Tag selection ajax call
var $tags = $('#tag-menu');

$tags.on('click', 'a.tag-link', function(e) {
  e.preventDefault();

  var tagId = $(this).attr('data-tag-id');

  $.ajax({
    url: 'me/',
    method: 'GET',
    data: {'tag_id': tagId},
    dataType: 'json',
    success: function(data) {
      clearPageEls();
      createPageEls(data);
    }
  });
});
