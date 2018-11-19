'use strict';


function createTagMenu(data) {
  // read in data from server, create and append tag menu elements
  var tagList = data;
  var tagMenu = [];
  for (var i = 0; i < tagList.length; i++) {
    var tag = tagList[i];
    var tagId = tag.tag_id;
    var tagName = tag.tag_name;
    var liEl = $('<li class="tag-indv"><a class="tag-link" href="me/" data-tag-id="' + tagId + '">' + tagName + '</a></li>');
    var ulEl = $('ul#tag-menu');
    ulEl.append(liEl);
  }
}

function clearTagMenu() {
  // clear tag menu
  var tags;
  tags = $('li.tag-indv');
  tags.remove()
}

// Search ajax call
var $input = $('input');

$input.on('keyup', function() {
  var searchText;
  searchText = $('#search').val();

  $.ajax({
    url: 'search/',
    method: 'GET',
    data: {'search' : searchText},
    dataType: 'json',
    success: function(data) {
      clearTagMenu();
      createTagMenu(data);
    }
  });
});

// On load--return all tags for drop down menu
$(function() {
  $.ajax({
    url: 'home/',
    method: 'GET',
    dataType: 'json',
    success: function(data) {
      createTagMenu(data);
    }
  });
});
