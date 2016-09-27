$(document).ready(function(){
  $('input[type="radio"][name="osn_select"]').change(function(){
    ($(this).val()=='instagram_posts') ? $('.instagram_option').show() : $('.instagram_option').hide();
  })
  $('input[type="radio"][name="osn_select"],#census-variable').change(function(){
    loadChoroplethData('tract_data.geojson','properties.'+$('input[type="radio"][name="osn_select"]:checked').val()+'.'+$('#census-variable').val());
  });
  $('input[type="radio"][name="osn_select"], input[type="checkbox"][name="show_heatmap"]').change(function(){
    $('input[type="checkbox"][name="show_heatmap"]').is(':checked') ? loadHeatMap($('input[type="radio"][name="osn_select"]:checked').val()) : removeHeatMap();
  });


  // This example requires the Visualization library. Include the libraries=visualization
  // parameter when you first load the API. For example:
  // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization">

  (function(window, document, $, undefined){
    // Access nested JSON object by string
    Object.byString = function(o, s) {
      s = s.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
      s = s.replace(/^\./, '');           // strip a leading dot
      var a = s.split('.');
      for (var i = 0, n = a.length; i < n; ++i) {
          var k = a[i];
          if (k in o) {
              o = o[k];
          } else {
              return null;
          }
      }
      return o;
    }

    var stateLayer, heatmap, map = new google.maps.Map(document.getElementById('map'), {
      zoom: 13,
      center: {lat: 34.0231837184805, lng: -118.481569383702},
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var loadChoroplethData =  function(file_name, variable) {
      if(stateLayer !== undefined) {
        stateLayer.forEach(function(feature) {
          stateLayer.remove(feature);
        });
      }
      stateLayer = loadMapShapes(file_name);
      var ranges = calculateRanges(file_name, variable);

      // update and display the legend
      document.getElementById('census-min').textContent =
          ranges.minValue.toLocaleString();
      document.getElementById('census-max').textContent =
          ranges.maxValue.toLocaleString();
      setStyleToStateLayer(stateLayer, variable, ranges);

      // Final step here sets the stateLayer GeoJSON data onto the map
      stateLayer.setMap(map);
      setListeners(stateLayer, variable, ranges);
    }

    loadChoroplethData('tract_data.geojson', 'properties.twitter_posts.count');

    function loadJson(file_name) {
      var jsonData;
      $.ajax({url: file_name, dataType: 'json', async: false, success: function(data) {
          jsonData = data;
        }
      });
      return jsonData;
    }

    function calculateRanges(file_name, variable) {
      var data = loadJson(file_name);
      return {
        minValue: data.features.map(el => Object.byString(el, variable)).filter(function(val) {return val !== null}).reduce((min, cur) => Math.min(min, cur), Infinity),
        maxValue: data.features.map(el => Object.byString(el, variable)).filter(function(val) {return val !== null}).reduce((max, cur) => Math.max(max, cur), -Infinity)
      }
    }

    /**
     * Takes a file_name and returns a maps.data object
     * Create the state data layer and load the GeoJson Data
     *
     * @param {string} file_name - The GeoJson file for loading layer data
     * @return {stateLayer object}
     */
    function loadMapShapes(file_name) {
      var stateLayer = new google.maps.Data();
      stateLayer.loadGeoJson(file_name);
      return stateLayer;
    }

    /**
     * Takes a stateLayer object and applies fillcolor for
     * different states
     *
     * @param {stateLayer object} stateLayer - The stateLayer object
     * @return null
     */
    function setStyleToStateLayer(stateLayer, variable, ranges) {
      // Set and apply styling to the stateLayer
      stateLayer.setStyle(styleFeature);
      function styleFeature(feature) {
        var low = [5, 69, 54];  // color of smallest datum
        var high = [151, 83, 34];   // color of largest datum

        // delta represents where the value sits between the min and max
        var delta = (Object.byString(feature, 'f.'+variable.split('.').slice(-2).join('.')) - ranges.minValue) /
            (ranges.maxValue - ranges.minValue);

        var color = [];
        for (var i = 0; i < 3; i++) {
          // calculate an integer color based on the delta
          color[i] = (high[i] - low[i]) * delta + low[i];
        }

        // determine whether to show this shape or not
        var showRow = true;

        var outlineWeight = 0.5, zIndex = 1;
        if (feature.getProperty('state') === 'hover') {
          outlineWeight = zIndex = 2;
        }

        return {
          strokeWeight: outlineWeight,
          strokeColor: '#fff',
          zIndex: zIndex,
          fillColor: 'hsl(' + color[0] + ',' + color[1] + '%,' + color[2] + '%)',
          fillOpacity: 0.75,
          visible: showRow
        };
      }
    }

    function setListeners(stateLayer, variable, ranges) {
      // set up the style rules and events for google.maps.Data
      stateLayer.addListener('mouseover', mouseInToRegion);
      stateLayer.addListener('mouseout', mouseOutOfRegion);

      /**
       * Responds to the mouse-in event on a map shape (state).
       *
       * @param {?google.maps.MouseEvent} e
       */
      function mouseInToRegion(e) {
        // set the hover state so the setStyle function can change the border
        e.feature.setProperty('state', 'hover');

        var percent = (Object.byString(e.feature, 'f.'+variable.split('.').slice(-2).join('.')) - ranges.minValue) /
            (ranges.maxValue - ranges.minValue) * 100;

        // update the label
        document.getElementById('data-label').textContent =
            'Tract #'+e.feature.getProperty('TRACT');
        document.getElementById('data-value').textContent =
            Object.byString(e.feature, 'f.'+variable.split('.').slice(-2).join('.')).toLocaleString();
        document.getElementById('data-box').style.display = 'block';
        document.getElementById('data-caret').style.display = 'block';
        document.getElementById('data-caret').style.paddingLeft = percent + '%';
      }

      /**
       * Responds to the mouse-out event on a map shape (state).
       *
       * @param {?google.maps.MouseEvent} e
       */
      function mouseOutOfRegion(e) {
        // reset the hover state, returning the border to normal
        e.feature.setProperty('state', 'normal');
      }
    }

    function getPoints(social_network) {
      var data = loadJson(social_network+'_09_12_2016.json.n'); var items = [];
      if(social_network.split('_')[0]=='instagram') {
        $.each(data, function(index) {
          if('latitude' in data[index].location) {
            items.push(new google.maps.LatLng(data[index].location.latitude, data[index].location.longitude));
          }
        });
      }
      else if(social_network.split('_')[0]=='twitter') {
        $.each(data, function(index) {
          items.push(new google.maps.LatLng(data[index].coordinates.coordinates[1], data[index].coordinates.coordinates[0]));
        });
      }
      return items;
    }
    var removeHeatMap = function() {
      (heatmap !== undefined) ? heatmap.setMap(null) : null;
    }
    var loadHeatMap = function(social_network) {
      removeHeatMap();
      heatmap = new google.maps.visualization.HeatmapLayer({
        dissipating: true,
        maxIntensity: 1,
        data: getPoints(social_network),
        map: map
      });
    }

    window.loadChoroplethData = loadChoroplethData;
    window.loadHeatMap = loadHeatMap;
    window.removeHeatMap = removeHeatMap;

  })(window, document, jQuery);
});