let map;
let marker;

var locations
var titles
var pictures

function setVariables(geo_location, title, picture){
  this.locations = geo_location
  this.titles = title
  this.pictures = picture
}

function initMap() {  
  map = new google.maps.Map(document.getElementById("map"), {
      zoom: 10,
      center: { lat: 30.024, lng: -97.887 },
    });

    var markers = [];
    for (let i = 0; i < locations.length; i++) {
        var lat_lng = locations[i].split(",");
        var lat = parseFloat(lat_lng[0].substring(1));
        var lng = parseFloat(lat_lng[1].slice(0,-1));
        var pos = new google.maps.LatLng(lat, lng);

        var marker = new google.maps.Marker({
            position: pos,
            map: map,
            id: i
        });

        var infowindow = new google.maps.InfoWindow();

        google.maps.event.addListener(marker, 'mouseover', (function(marker, i) {
            return function() {
                infowindow.setContent(title[i] + "<br><img src='https://storage.googleapis.com/apad-group8-bucket/img/reviews/" + pictures[i] + "'width=100px height=100px>"); infowindow.open(map, marker);
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
