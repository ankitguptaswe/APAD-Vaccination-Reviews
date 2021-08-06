let map;
let marker;

function initMap() {
    // _args = Args;
    // const locations = [_args][0][0];
    // alert(locations);

    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 10,
      center: { lat: 30.024, lng: -97.887 },
    });

    const locations = [
      {lat: 13, lng: 13},
        {lat: 13, lng: 13},
          {lat: 13, lng: 13},
            {lat: 13, lng: 13}
    ];

    var markers = [];
    console.log(locations);
    for (let i = 0; i < 4; i++) {

        // var array = locations[0][0][i];
        // var array2 = array.split(",");
        // var lat = array2[0].substring(1);
        // var lng = array2[1].slice(0,-1);



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
