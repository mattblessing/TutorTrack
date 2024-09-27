function changeDetails() {
  // Get name and childID
  var name = $(this).text();
  var childID = $("#childInput").val();
  if (name != "No topics currently exist for this child! Create a topic!") {
    window.location.replace("/topic/" + childID + "/" + name); // Redirect user to change topic details page
  }
}

$(document).ready(function () {

  $("#childInput").on("change", function () {
    $.ajax({
      type: "POST",
      url: "/view/topics",
      data: {
        child: $("#childInput").val()
      },
      success: function (e) {
        Highcharts.charts[0].series[0].setData([]); // Update hierarchy chart display
        Highcharts.charts[0].series[0].setData(e.data);
        $(".highcharts-label").click(changeDetails); // Assign change details function to each topic in chart
      }
    });
  });

  Highcharts.chart("container", {
    chart: {
      height: 530,
      inverted: true
    },
    title: {
      text: ""
    },
    series: [{
      type: "organization",
      name: "Topics",
      keys: ["from", "to"],
      data: data,
      colorByPoint: false,
      color: "silver",
      dataLabels: {
        color: "black"
      },
      borderColor: "white",
      nodeWidth: 65
    }],
    tooltip: {
      outside: true
    },
    exporting: {
      allowHTML: true,
      sourceWidth: 800,
      sourceHeight: 600
    }

  });

  $(".highcharts-label").click(changeDetails); // Assign change details function to each topic in chart

});

