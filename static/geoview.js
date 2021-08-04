let map;
let marker;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 10,
      center: { lat: 30.024, lng: -97.887 },
    });

    var markers = [];
    for (var i = 0; i < locations.length; i++) {
        var pos = new google.maps.LatLng(locations[i].lat, locations[i].lng);

        var marker = new google.maps.Marker({
            position: pos,
            map: map,
            id: i
        });

        var infowindow = new google.maps.InfoWindow();

        google.maps.event.addListener(marker, 'mouseover', (function(marker, i) {
            return function() {
                infowindow.setContent("<img src='static/img/" + (i+1) + ".png' width=100px height=100px>"); infowindow.open(map, marker);
            }
        })(marker, i));
        google.maps.event.addListener(marker, 'mouseout', function () {
            infowindow.close();
        });
        markers.push(marker);
    }

    // Add a marker clusterer to manage the markers.
    new MarkerClusterer(map, markers, {
      imagePath:
        "https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m",
    });
  }
  const locations = [
    { lat: 30.03233, lng: -97.982398 },
    { lat: 30.03989, lng: -97.238389 },
    { lat: 30.02787, lng: -97.232023 },
    { lat: 30.02894, lng: -97.233434 },
    { lat: 30.03444, lng: -97.216968 },
  ];

initMap();
