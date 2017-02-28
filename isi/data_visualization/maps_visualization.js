$(document).ready(function(){
  var census_variables = ['meanP','meanN','meanV','meanA','meanD','population16','employment','employment_percent','median_household','means_household','cash_public','food_stamp','med_age','age_me','num_of_users','num_of_tweets','bachelor','bachelor_percent','gyrByCensus','Automobile','Drove_Alone','Public_Transit','Walking','Bicycle','Other','Worked_Home','No_vehicle','One_vehicle','Two_vehicles','Three_vehicles','HoursPerWeek','Quintile_3Mbps','Total_Drivers','Mean_Travel_Time_min','not_alone','medlog','pubtrans','HO_vacancy_rate','Rental_vacancy_rate','median_rooms','Owner_occupied','Renter_occupied','Average_household_OO','Average_household_RO','OPR_____1_00','OPR__1_x__1_5','OPR_____1_51','Mortgage_units','Per_mortgage_OO','HH_Size','One_vehicle_plus', 'gang_related', 'gang_unrelated', '0321_Robbery_Knife_Street_Hwy', '0922_Arson_Other_Resd_Uninhab', '0336_Robbery_Othr_Wpn_Bank', '0325_Robbery_Knife_Residential', '0690_Larceny___Other', '0300_Robbery___General', '0511_Burglary_Force_Resd', '0341_Robbery_Strongarm_Street_Hwy', 'Public_Intoxication_', 'Larceny___Bicycle_', '2622_Cruelty_to_Animals', '0522_Burglay_Unlaw_Entry_Non_Resd', '1820_Narco_Possess_Unspecified_Drug', '0610_Larceny___Pickpocket', '2619_Unfair_Business_Practices', '1823_Narco_Possess_Synthetic', '0322_Robbery_Knife_Commercial', '0981_Arson_Motor_Vehicle', '0331_Robbery_Othr_Wpn_Street_Hwy', '2614_Trespass_Illegal_Entry', '0630_Larceny___Shoplift', '0344_Robbery_Strongarm_Store', '2610_Possess_Drug_Paraphernalia', '1813_Narco_Sales_Synthetic', '1811_Narco_Sales_Opiate_Cocaine', '0333_Robbery_Othr_Wpn_Gas_Station', '0660_Larceny___Bicycle', '2400_Disorderly_Conduct', '1821_Narco_Possess_Opiate_Cocaine', '0531_Burglary_Attempt___Resd', 'Contempt_of_Court_', '1800_Narcotics___General', '0730_GTA___Other_Vehicle', '0317_Robbery_Firearm_Other_Loc', '0512_Burglary_Force_Non_Resd', '0326_Robbery_Knife_Bank', '2612_Public_Nuisances', '0343_Robbery_Strongarm_Gas_Station', '1824_Narco_Possess_Other', '2623_Other_Animal_Crimes', '2000_Family_Offenses', '0532_Burglary_Attempt___Non_Resd', '2604_Blackmail_Extortion', '0400_Agg_Assault___General', 'Simple_Assault_', '0337_Robbery_Othr_Wpn_Other_Loc', '2600_All_Other_Offenses', '0620_Larceny___Purse_snatch', '2607_Federal_Violation', '2606_Contempt_of_Court', '2625_Viol_of_Regulatory_Laws', '0335_Robbery_Othr_Wpn_Residential', '0650_Larceny___Vehicle_Parts_Acc', '1300_Recv_Poss_Stolen_Property', '0450_Simple_Assault', '2602_Kidnapping_Abduction', '0420_Agg_Assault___Knife', '2300_Public_Intoxication', '0962_Arson_Public_Bldg_Uninhab', '0316_Robbery_Firearm_Bank', '2626_Municipal_Code_Violation', '0700_GTA___Recovery', '0521_Burglay_Unlaw_Entry_Resd', '2800_Juvenile_Curfew_Loitering_', '0720_GTA___Comm_Vehicle', '0990_Arson_All_Others', '1822_Narco_Possess_Marijuana', '0332_Robbery_Othr_Wpn_Commercial', '0972_Arson_Other_Structure_Uninhab', '0710_GTA___Passenger_Car', '0430_Agg_Assault___Othr_Wpn', 'Larceny___Pickpocket_', '0342_Robbery_Strongarm_Commercial', '0640_Larceny___From_Vehicle', '2621_Aiding_Abetting_Crimes', '1700_Sex_Offenses___Other', '0500_Burglary___General', '0680_Larceny___From_Coin_Machine', '0670_Larceny___From_Building', '0315_Robbery_Firearm_Residential', '2611_Possess_Obscene_Literature', '0346_Robbery_Strongarm_Bank', 'Family_Offenses_', '0410_Agg_Assault___Firearm', '1810_Narco_Sales_Unspecified_Drug', '0314_Robbery_Firearm_Conv_Store', '2630_Misappropriation_of_Property', 'Larceny___Other_', '0327_Robbery_Knife_Other_Loc', '2609_Possess_Burglary_Tool', '0921_Arson_Other_Resd_Inhab', '2601_Contributing_Delinq_Minor', '0334_Robbery_Othr_Wpn_Conv_Store', '1500_Carry_Poss_Weapon', '0311_Robbery_Firearm_Street_Hwy', '0324_Robbery_Knife_Conv_Store', '0312_Robbery_Firearm_Commercial', 'Forgery_Counterfeit_', '1000_Forgery_Counterfeit', '2200_Liquor_Law_Violations', '0347_Robbery_Strongarm_Other_Loc', '0440_Agg_Assault___Hands', '0912_Arson_Single_Fam_Resd_Uninhab', '1812_Narco_Sales_Marijuana', '2620_Telecom_Utility_Violations', '0345_Robbery_Strongarm_Residential'];
  for(index in census_variables) {
    $('#census-variable').append('<option value='+census_variables[index]+'>'+census_variables[index]+'</option>');
  }
  $('input[type="radio"][name="osn_select"]').change(function(){
    ($(this).val()=='instagram_posts') ? $('.instagram_option').show() : $('.instagram_option').hide();
  })
  $('input[type="radio"][name="osn_select"],#census-variable').change(function(){
    loadChoroplethData('tract_data_news_2014_polices.geojson','properties.'+$('input[type="radio"][name="osn_select"]:checked').val()+'.'+$('#census-variable').val());
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
      s = loadJson(file_name);
      console.log(ranges);
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

    loadChoroplethData('tract_data_news_2014_polices.geojson', 'properties.twitter_posts.count');

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
      stateLayer.addListener('click', openImage);

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

      /**
       * Responds to the click event on a map shape (state).
       * Opens up the corresponding analysis for tract
       *
       * @param {?google.maps.MouseEvent} e
       */
      function openImage(e) {
        // open image in new tab
        if($('#crime_data_analysis_types').val()==="All") {
          $('#crime_data_analysis_types option').each(function(){
            if($(this).val()=="All") return true;
            window.open('/Tract '+e.feature.f.TRACT+', '+variable.split('.')[1]+$(this).val()+'.png', '_blank');
          });
        }
        else {
          window.open('/Tract '+e.feature.f.TRACT+', '+variable.split('.')[1]+$('#crime_data_analysis_types').val()+'.png', '_blank');
        } 
      }
    }
    function getPoints(social_network) {
      var data = loadJson(social_network+'_11_07_2016.json.n'); var items = [];//console.log(data);
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