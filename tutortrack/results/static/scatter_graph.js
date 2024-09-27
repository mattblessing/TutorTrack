$(document).ready(function () {

    function addData(chart, label, data) { // Add new data item to scatter graph
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(data);
        chart.update();
    }

    function addRegression(chart, label, data) { // Add new regression line data item to scatter graph
        chart.data.labels.push(label);
        chart.data.datasets[1].data.push(data);
        chart.update();
    }

    function removeData(chart) { // Remove all data from scatter graph
        chart.data.labels.pop();
        chart.data.datasets.forEach((dataset) => {
            dataset.data = [];
        });
        chart.update();
    }

    Chart.defaults.global.elements.line.fill = false;
    Chart.defaults.global.legend.display = false;
    var chart = new Chart(ctx, {
        type: "scatter",
        data: {
            labels: labels,
            datasets: [{
                backgroundColor: "rgb(255, 99, 132)",
                borderColor: "rgb(255, 99, 132)",
                data: data,
                borderWidth: 1,
                showLine: true
            }, {
                backgroundColor: "rgb(255, 99, 132)",
                borderColor: "rgb(255, 99, 132)",
                data: [{ x: 1, y: y1 }, { x: results.length, y: y2 }],
                borderWidth: 1,
                showLine: false,
                pointRadius: 0
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    bounds: "ticks",
                    ticks: {
                        stepSize: 1
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Number of Results Logged (Quantity of Work Completed)"
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        max: 100
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Percentage Score (%)"
                    }
                }]
            },
            elements: {
                line: {
                    tension: 0
                }
            }
        }
    });

    $("#childInput").on("change", function () {
        var child = $(this).val();
        $.ajax({
            type: "POST",
            url: "/results/scatter/graph",
            data: {
                child: child,
                childChange: true
            },
            success: function (data) {
                $("#topicInput").empty()
                $.each(data.topics, function (index, choice) { // Set new topic selection options
                    $("#topicInput").append($("<option></option>").attr("value", choice[0]).text(choice[1]));
                });
                $("#topicInput").val($("#topicInput option:first").val());
                if (data.results.length >= 3) { // Only show graph if 3 or more results logged
                    chart.data.datasets[1].showLine = false;
                    chart.data.datasets[0].showLine = true;
                    chart.update();
                    $("#myChart").show();
                    $("#notEnoughResults").text("");
                    removeData(chart);
                    var labels = [];
                    var newData = [];
                    for (i = 0; i < data.results.length; i++) { // Set up new data and labels for graph
                        labels.push(i + 1);
                        newData.push({ x: i + 1, y: data.results[i][6] })
                    }
                    for (i = 0; i < newData.length; i++) { // Add data points to graph
                        addData(chart, labels[i], newData[i]);
                    }
                    // Add first point of regression line
                    addRegression(chart, 1, { x: 1, y: data.coefficients[0] + data.coefficients[1] * 1 });
                    // Add second point of regression line
                    addRegression(chart, newData.length, { x: newData.length, y: data.coefficients[0] + data.coefficients[1] * newData.length });
                    if (data.topicLength == 1) { // If topic has no subtopics
                        $("#toggleLine").show();
                        $("#toggleLine").text("Line of best fit");
                    } else {
                        $("#toggleLine").hide();
                    }
                } else {
                    $("#myChart").hide();
                    $("#notEnoughResults").text("There are currently not enough results for that topic.");
                    $("#toggleLine").hide();
                }
            }
        });
    });
    $("#topicInput").on("change", function () {
        var child = $("#childInput").val();
        var topic = $(this).val();
        $.ajax({
            type: "POST",
            url: "/results/scatter/graph",
            data: {
                child: child,
                topic: topic,
                topicChange: true
            },
            success: function (data) {
                if (data.results.length >= 3) { // Only show graph if 3 or more results logged
                    chart.data.datasets[1].showLine = false;
                    chart.data.datasets[0].showLine = true;
                    chart.update();
                    $("#myChart").show();
                    $("#notEnoughResults").text("");
                    removeData(chart);
                    var labels = [];
                    var newData = [];
                    for (i = 0; i < data.results.length; i++) { // Setting up new data and labels for graph
                        labels.push(i + 1);
                        newData.push({ x: i + 1, y: data.results[i][6] })
                    }
                    for (i = 0; i < newData.length; i++) { // Add data points to graph
                        addData(chart, labels[i], newData[i]);
                    }
                    // Add first point of regression line
                    addRegression(chart, 1, { x: 1, y: data.coefficients[0] + data.coefficients[1] * 1 });
                    // Add second point of regression line
                    addRegression(chart, newData.length, { x: newData.length, y: data.coefficients[0] + data.coefficients[1] * newData.length });
                    if (data.topicLength == 1) { // If topic has no subtopics
                        $("#toggleLine").show();
                        $("#toggleLine").text("Line of best fit");
                    } else {
                        $("#toggleLine").hide();
                    }
                } else {
                    $("#myChart").hide();
                    $("#notEnoughResults").text("There are currently not enough results for that topic.");
                    $("#toggleLine").hide();
                }
            }
        });
    });

    if (data.length < 3) { // Only show graph if 3 or more results logged
        $("#toggleLine").hide();
        $("#myChart").hide();
        $("#notEnoughResults").text("There are currently not enough results for that topic.");
    } else {
        if (topicLength == 1) { // If topic has no subtopics
            $("#toggleLine").show();
            $("#toggleLine").text("Line of best fit");
        } else {
            $("#toggleLine").hide();
        }
    }

    $("#toggleLine").on("click", function () {
        if (chart.data.datasets[0].showLine == false) {
            chart.data.datasets[1].showLine = false;
            chart.data.datasets[0].showLine = true;
            chart.update();
            $("#toggleLine").text("Line of best fit")
        } else {
            chart.data.datasets[0].showLine = false;
            chart.data.datasets[1].showLine = true;
            chart.update();
            $("#toggleLine").text("Connect points")
        }
    });

});