$(document).ready(function () {

    function addData(chart, data) { // Add new data item to histogram
        chart.data.datasets[0].data.push(data);
        chart.update();
    }

    function removeData(chart) { // Remove all data from histogram
        chart.data.datasets.forEach((dataset) => {
            dataset.data = [];
        });
        chart.update();
    }

    Chart.defaults.global.legend.display = false;
    var chart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            datasets: [{
                backgroundColor: "rgb(255, 99, 132)",
                borderColor: "rgb(255, 99, 132)",
                data: data
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    display: false, // Axis for the bars - so they fill the groups
                    barPercentage: 1.3,
                    ticks: {
                        max: 90
                    }
                }, {
                    display: true, // Axis for the x axis labels
                    ticks: {
                        autoSkip: false,
                        max: 100
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Percentage Score (%)"
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        stepSize: 1
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Number of Results"
                    }
                }]
            },
            responsive: true, // Set chart to fill its container
            tooltips: {
                enabled: false
            }
        }
    });

    $("#childInput").on("change", function () {
        var child = $(this).val();
        var startDate = $("#startDateInput").val();
        var endDate = $("#endDateInput").val();
        $.ajax({
            type: "POST",
            url: "/reports",
            data: {
                child: child,
                startDate: startDate,
                endDate: endDate,
                childChange: true
            },
            success: function (data) {
                $("#topicInput").empty()
                $.each(data.topics, function (index, choice) { // Set new topic selection options
                    $("#topicInput").append($("<option></option>").attr("value", choice[0]).text(choice[1]));
                });
                $("#topicInput").val(0); // Set default selection to "All topics"
                $("#reportName").text(data.childName + " - Report");
                removeData(chart);
                for (i = 0; i < data.histogramData.length; i++) { // Update chart data
                    addData(chart, data.histogramData[i]);
                }
                $("#topicBreakdown").html(data.topicBreakdown); // Display new topic breakdown section
                $("#reportSent").text("");
            }
        });
    });
    $("#topicInput").on("change", function () {
        var child = $("#childInput").val();
        var topic = $(this).val();
        var startDate = $("#startDateInput").val();
        var endDate = $("#endDateInput").val();
        $.ajax({
            type: "POST",
            url: "/reports",
            data: {
                child: child,
                topic: topic,
                startDate: startDate,
                endDate: endDate,
                topicChange: true
            },
            success: function (data) {
                removeData(chart);
                for (i = 0; i < data.histogramData.length; i++) { // Update chart data
                    addData(chart, data.histogramData[i]);
                }
                $("#reportSent").text("");
            }
        });
    });
    $("#submit").on("click", function () { // Date range changed
        var child = $("#childInput").val();
        var topic = $("#topicInput").val();
        var startDate = $("#startDateInput").val();
        var endDate = $("#endDateInput").val();
        $.ajax({
            type: "POST",
            url: "/reports",
            data: {
                child: child,
                topic: topic,
                startDate: startDate,
                endDate: endDate,
                dateChange: true
            },
            success: function (data) {
                if (data.error) { // Display validation message
                    $("#startDateInput").addClass("is-invalid");
                    $("#endDateInput").addClass("is-invalid");
                    $("#dateError").text("Invalid date range.");
                } else { // Remove validation message if there is one
                    $("#startDateInput").removeClass("is-invalid");
                    $("#endDateInput").removeClass("is-invalid");
                    $("#dateError").text("");
                    removeData(chart);
                    for (i = 0; i < data.histogramData.length; i++) { // Update chart data
                        addData(chart, data.histogramData[i]);
                    }
                    $("#topicBreakdown").html(data.topicBreakdown); // Display new topic breakdown section
                }
                $("#reportSent").text("");
            }
        });
    });
    $("#sendReport").on("click", function () {
        var child = $("#childInput").val();
        var topic = $("#topicInput").val();
        var startDate = $("#startDateInput").val();
        var endDate = $("#endDateInput").val();
        $.ajax({
            type: "POST",
            url: "/reports",
            data: {
                child: child,
                topic: topic,
                startDate: startDate,
                endDate: endDate,
                sendReport: true
            },
            success: function (data) {
                // Flash message for report send confirmation
                $("#reportSent").append('<div class="alert alert-success">' + data.success + "</div>");
            }
        });
    });
});

