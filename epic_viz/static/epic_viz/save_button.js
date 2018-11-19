'use strict';

$('#csv').on('click', function() {
  var xhttp;
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    var a, today;
    if (xhttp.readyState === 4 && xhttp.status === 200) {
      a = document.createElement('a');
      a.href = window.URL.createObjectURL(xhttp.response);
      today = new Date();
      a.download = 'epic_output_' + today.toDateString().split(' ').join('_') + '.xlsx';
      a.style.display = 'none';
      document.body.appendChild(a);
      return a.click();
    }
  };
  xhttp.open('GET', '/csv', true);
  xhttp.setRequestHeader('Content-Type', 'application/json');
  xhttp.responseType = 'blob';
  xhttp.send();
});
