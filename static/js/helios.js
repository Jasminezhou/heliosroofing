$(function() {
  function slideByClick(event) {
    var dom = event.target;
    var target = [];
    if (($(dom).prop("tagName") === "A") &&location.pathname.replace(/^\//,'') == dom.pathname.replace(/^\//,'') && location.hostname == dom.hostname) {
      target = $(dom.hash);
      target = target.length ? target : $('[name=' + dom.hash.slice(1) +']');
    } else if (dom.dataset.href || dom.parentNode.dataset.href) {
      target = $(dom.dataset.href || dom.parentNode.dataset.href);
    }
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top - 50
        }, 1000);
        return false;
      }
  }


  // services collapse panel control
  function showService(e) {
    var target = e.target.dataset.toggleclass || $(e.currentTarget).data("toggleclass");
    if (!$('.'+target).hasClass("collapse in")) {
        // #target is summary section; .target is responsive detail section
        $("#services .service_summary").css("background-color", "");
        $("#services .collapse").collapse("hide");
        $('#'+target).css('background-color', "lightgrey");
        $('.'+target).collapse("show");
    }
  }
  // service detail wrapper toggle
  function showServiceWrapper(e) {
    if (($(".service_detail_wrapper:hidden").length !== 1) || ($(".service_detail_wrapper:hidden").attr("id") === e.currentTarget.parentElement.id) || ($(".service_detail_wrapper:hidden").attr("id") === e.currentTarget.dataset.category)) {
        $(".service_detail_wrapper").hide();
        if (e.currentTarget.parentElement.id === "residential" || e.currentTarget.dataset.category === "residential") {
            $(".service_detail_wrapper#residential").slideDown();
        } else if (e.currentTarget.parentElement.id == "commercial" || e.currentTarget.dataset.category === "commercial") {
            $(".service_detail_wrapper#commercial").slideDown();
        }
    }
  }


  $("#services .collapse").collapse({
      toggle: false
  });
  $("#services .service_summary").click(function(e) {
      showService(e);
  });


  // service map
  $(".service_map_group").each(
          function(i, g) {
              $($(g).data('details').split(',')).each(
                  function(i, d) {
                      $(d).hide();
                  });
          });
  $(".service_detail_wrapper").hide();
  // click events
  $(".service_map_group").click(function(){
    var detail_id = $(this).data("details");
    $(detail_id).toggle("slow");
  });
  $(".service_map_detail, .service_menu_detail").click(function(e){
    if (location.pathname.split('/').length > 2) {
      location.href = '/#services';
    } else {
      showServiceWrapper(e);
      showService(e);
      slideByClick(e);
    }

  });
  // hover events
  $(".service_map_detail").qtip({
    position: {
        target: 'mouse'
    }
  });

  $('a[href*=#]:not([href=#])').click(function(event) {
      slideByClick(event);
  });

  // chat box


    box = $("#chat-box").chatbox({id:"chat-box",
                                  user:{key : "value"},
                                  title : "Chat Now",
                                  offset: "15px",
                                  width: 270,
                                    introPhoto: "./static/img/expert.jpg",
                                    introName: "Jovi",
                                    introDescription: "Helios Roofing expert",
    });


  // Weather bar
  /*[{"data":
   *    {"pop": 55.00000000000001,
   *     "icon": "partly-cloudy-day",
   *     "summary": "Mostly cloudy throughout the day.",
   *     "temperatureMax": 18.78,
   *     "windSpeed": 4.3,
   *     "temperatureMin": 13.06,
   *     "services": ["roof_repair"]
   *    },
   *  "day":
   *    {
   *     "weekday": "Thursday",
   *     "date": "14-07-03"
   *    }
   * },
   * ...
   *]
   *
   * */
  var tr_dates = [];
  var tr_weather = [];
  var tr_services = [];
  var tr_services_temp = [];
  var short_weekdays = [ "SUN", "MON", "TUE", "WED", "THR", "FRI", "SAT"];
  var formatted_month = function(d) { return (d.getMonth() < 9 ? '0' : '') + (d.getMonth() + 1); };
  var formatted_day = function(d) { return (d.getDate() < 10 ? '0' : '') + d.getDate(); };
  var service_duration = {
    "roof_repair": 3,
    "gutter_fix": 1,
    "inspection": 1,
    "default_service": 1
  };
  var service_name = {
    'roof_repair': "Repairing Roof",
    'gutter_fix': "Gutter Maintenance",
    'inspection': "Project Inspection",
    'default_service': "Repair and Maintenance"
  };

  $.getJSON( "http://jingweather.appspot.com/api/helios", function(data) {
    $.each(data, function(i, w){
        // tr_dates
        var d = new Date(w.day.date);
        tr_dates.push([short_weekdays[d.getDay()], formatted_month(d)+'/'+formatted_day(d)]);
        // tr_weather
        tr_weather.push("./static/img/"+w.data.icon+".png");
        // tr_services
        tr_services_temp.push(w.data.services[0] || "default_service");
    });
    //tr_services
    var c = 0; //counter
    tr_services_temp.forEach(function(s,i){
        if (c === 0) {
           tr_services.push([service_duration[s], s, service_name[s]]);
           c = service_duration[s]-1;
          } else {
            --c;
          }
        });
    console.log(tr_services_temp, tr_services);
    // render the widget
    $.each(tr_dates, function(i, d) {
        $("#weatherBar tr#dates").append("<th>"+d[0]+" </br><span class='date'>"+d[1]+"</span></th>");
    });
    $.each(tr_weather, function(i, w) {
        $("#weatherBar tr#weather").append('<th><img src='+w+'></th>');
    });
    $.each(tr_services, function(i, s) {
        $("#weatherBar tr#services").append("<td colspan="+s[0]+" class='project_service "+s[1]+"'>"+s[2]+"</td>");
    });

  });

});
