from flask import render_template, request, Blueprint, jsonify
from sqlalchemy import text
from tutortrack import db
from tutortrack.models import login_required
from tutortrack.utils import (
    getChildrenSelectList, getTopicSelectList, tutorGetResults
)
from tutortrack.reports.forms import ReportForm
from tutortrack.reports.utils import (
    getHistogramData, getMeans, createRevisionList
)
from tutortrack.email import sendAttachmentEmail
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from quickchart import QuickChart
import datetime
import os

reports = Blueprint(
    "reports", __name__, template_folder="templates", static_folder="static",
    static_url_path="/reports/static"
)


@reports.route("/reports", methods=["GET", "POST"])
@login_required(type="tutor")
def view_reports():
    # Set up the different selections on the page
    form = ReportForm()
    children = getChildrenSelectList()
    form.child.choices = children  # Set child options for tutor
    if len(children) != 0:
        topicList = getTopicSelectList(children[0][0], True)
        results = tutorGetResults(children[0][0], "0", None, None)
    else:
        topicList = []
        results = []

    # Set the topic selection choices for the histogram display
    form.topic.choices = topicList
    # Set end date for default report
    form.endDate.data = datetime.date.today()
    histogram = getHistogramData(results)

    if len(results) != 0:
        # Set start date for default report
        form.startDate.data = datetime.datetime.strptime(
            results[len(results)-1][4], "%Y-%m-%d"
        )
        # Get mean score for each topic
        meanScores = getMeans(
            children[0][0], topicList,
            datetime.datetime.strptime(
                results[len(results)-1][4], "%Y-%m-%d"
            ).strftime("%Y-%m-%d"),
            datetime.date.today().strftime("%Y-%m-%d")
        )
        # Get revision list
        revision = createRevisionList(
            children[0][0], meanScores,
            datetime.datetime.strptime(
                results[len(results)-1][4], "%Y-%m-%d"
            ).strftime("%Y-%m-%d"),
            datetime.date.today().strftime("%Y-%m-%d")
        )
    else:
        # Set start date to first day of current year
        form.startDate.data = datetime.datetime.strptime(
            str(datetime.date.today().year)+"-01-01", "%Y-%m-%d"
        )
        meanScores = []
        revision = []

    # When child selection is changed
    if request.method == "POST" and "childChange" in request.form:
        # Get new results for selection
        results = tutorGetResults(
            request.form["child"], "0", request.form["startDate"],
            request.form["endDate"]
        )
        # Get topics for the particular child
        topicList = getTopicSelectList(request.form["child"], True)
        # Get data list to go into histogram
        histogram = getHistogramData(results)
        # Get mean score for each topic
        meanScores = getMeans(
            request.form["child"], topicList, request.form["startDate"],
            request.form["endDate"]
        )
        # Get revision list
        revision = createRevisionList(
            request.form["child"], meanScores, request.form["startDate"],
            request.form["endDate"]
        )
        if len(results) != 0:
            return jsonify({
                "topics": topicList,
                "childName": results[0][1]+" "+results[0][2],
                "histogramData": histogram,
                "topicBreakdown": render_template(
                    "topic_breakdown.html", meanScores=meanScores,
                    revisionList=revision
                )
            })
        else:
            with db.engine.connect() as conn:
                childName = conn.execute(
                    text("SELECT * FROM Child WHERE ChildID=:id"),
                    {"id": request.form["child"]}
                ).fetchall()
            return jsonify({
                "topics": topicList,
                "childName": childName[0][1]+" "+childName[0][2],
                "histogramData": histogram,
                "topicBreakdown": render_template(
                    "topic_breakdown.html", meanScores=meanScores,
                    revisionList=revision)
            })
    # When topic selection is changed
    elif request.method == "POST" and "topicChange" in request.form:
        # Get new results and histogram data for selection
        results = tutorGetResults(
            request.form["child"], request.form["topic"],
            request.form["startDate"], request.form["endDate"]
        )
        histogram = getHistogramData(results)
        return jsonify({"histogramData": histogram})
        # When date range is changed
    elif request.method == "POST" and "dateChange" in request.form:
        startDate = request.form["startDate"]
        endDate = request.form["endDate"]
        try:
            # If startDate > endDate or endDate > current date
            if (
                datetime.datetime.strptime(startDate, "%Y-%m-%d") >
                datetime.datetime.strptime(endDate, "%Y-%m-%d") or
                datetime.datetime.strptime(endDate, "%Y-%m-%d") >
                datetime.datetime.today()
            ):
                return jsonify({"error": "invalidDates"})
        except ValueError:
            # A ValueError will be thrown if the text entered cannot be
            # converted to a datetime object
            return jsonify({"error": "notDates"})
        # Get new results and histogram data for selection
        results = tutorGetResults(
            request.form["child"], request.form["topic"], startDate, endDate
        )
        histogram = getHistogramData(results)
        # Get mean score for each topic
        topicList = getTopicSelectList(request.form["child"])
        topicList.insert(0, (0, "All topics"))
        meanScores = getMeans(
            request.form["child"], topicList, startDate, endDate
        )
        # Get revision list
        revision = createRevisionList(
            request.form["child"], meanScores, startDate, endDate
        )
        return jsonify({
            "histogramData": histogram,
            "topicBreakdown": render_template(
                "topic_breakdown.html", meanScores=meanScores,
                revisionList=revision
            )
        })
    # When "Send Report" is pressed
    elif request.method == "POST" and "sendReport" in request.form:
        # Get child and parent details
        with db.engine.connect() as conn:
            child = conn.execute(text(
                "SELECT Child.Firstname, Child.Surname, User.Email, " +
                "User.Firstname " +
                "FROM Child, User " +
                "WHERE ChildID=:cID AND User.UserID=Child.ParentID"
            ),
                {"cID": request.form["child"]}
            ).fetchall()
            # Get selected topic details
            histogramTopic = conn.execute(text(
                "SELECT Name, ParentTopicID " +
                "FROM Topic, ChildTopic " +
                "WHERE Topic.TopicID=:tID AND Topic.TopicID=" +
                "ChildTopic.TopicID AND ChildTopic.ChildID=:cID"
            ),
                {"tID": request.form["topic"], "cID": request.form["child"]}
            ).fetchall()
        # Get topics for the particular child
        topicList = getTopicSelectList(request.form["child"])
        # Get new results and histogram data for selection
        results = tutorGetResults(
            request.form["child"], request.form["topic"],
            request.form["startDate"], request.form["endDate"]
        )
        histogram = getHistogramData(results)
        # Get mean score for each topic
        meanScores = getMeans(
            request.form["child"], topicList, request.form["startDate"],
            request.form["endDate"]
        )
        # Get revision list
        revision = createRevisionList(
            request.form["child"], meanScores, request.form["startDate"],
            request.form["endDate"]
        )

        # Create chart to be turned into an image (creates the same
        # chart as the one displayed on front end)
        chart = QuickChart()
        chart.width = 2000
        chart.height = 1000
        chart.config = {
            "type": "bar",
            "data": {
                "labels": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                "datasets": [{
                    "backgroundColor": "rgb(255, 99, 132)",
                    "borderColor": "rgb(255, 99, 132)",
                    "data": histogram
                }]
            },
            "options": {
                "scales": {
                    "xAxes": [{
                        "display": False,
                        "barPercentage": 1.3,
                        "ticks": {
                            "max": 90
                        }
                    }, {
                        "display": True,
                        "ticks": {
                            "autoSkip": False,
                            "max": 100,
                            "fontSize": 40
                        },
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Percentage Score (%)",
                            "fontSize": 40
                        }
                    }],
                    "yAxes": [{
                        "ticks": {
                            "beginAtZero": True,
                            "stepSize": 1,
                            "fontSize": 40
                        },
                        "scaleLabel": {
                            "display": True,
                            "labelString": "Number of Results",
                            "fontSize": 40
                        }
                    }],
                },
                "legend": False,
                "responsive": True,
                "tooltips": {
                    "enabled": False
                }
            }
        }
        # Save the histogram as file on disk
        chart.to_file("histogram.png")

        startDate = request.form["startDate"].replace("/", "")
        endDate = request.form["endDate"].replace("/", "")

        # Register the font for the canvas
        pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))

        # Page information
        page_width = 2156
        page_height = 600 + 80*len(meanScores) + 170 + 80*len(revision) + 1400
        margin = 100

        # Create and name the .pdf file
        c = canvas.Canvas(
            child[0][0]+"_"+child[0][1]+"_"+startDate+"_"+endDate+".pdf"
        )
        c.setPageSize((page_width, page_height))

        # Title
        c.setFont("Arial", 80)
        title = "Progress Report"
        title_width = stringWidth(title, "Arial", 80)
        c.drawString((page_width-title_width)/2, page_height - margin*2, title)
        y = page_height - margin*3.5
        x = 2*margin

        # Report details
        c.setFont("Arial", 50)
        c.drawString(x, y, "Child Name:")
        c.setFont("Arial", 45)
        c.drawString(x + 550, y, child[0][0]+" "+child[0][1])
        y -= margin*0.8

        c.setFont("Arial", 50)
        c.drawString(x, y, "Date Range:")
        c.setFont("Arial", 45)
        c.drawString(
            x + 550, y, request.form["startDate"]+" - "+request.form["endDate"]
        )
        y -= margin*1.2

        # Topic breakdown
        c.setFont("Arial", 60)
        c.drawString(x, y, "Topic Breakdown")
        y -= margin

        for topic in meanScores:
            c.setFont("Arial", 45)
            if str(topic[1]) == "0":
                c.drawString(x, y, "<strong>"+topic[0]+"</strong>")
            else:
                c.drawString(x, y, topic[0])
            c.setFont("Arial", 38)
            c.drawString(x + 900, y, "Mean Score: "+str(topic[1])+"%")
            c.drawString(
                x + 1300, y, "Number of Results Logged: "+str(topic[2])
            )
            y -= margin*0.8
        y -= margin*0.5

        # Revision list
        c.setFont("Arial", 60)
        c.drawString(x, y, "Revision List")
        y -= margin

        c.setFont("Arial", 45)
        for topic in revision:
            c.drawString(x, y, topic[0])
            y -= margin*0.8
        y -= margin*0.5

        # Histogram
        c.setFont("Arial", 60)
        c.drawString(x, y, "Spread of Scores")
        y -= margin
        c.setFont("Arial", 50)
        c.drawString(x, y, "Topic:")
        c.setFont("Arial", 45)
        if len(histogramTopic) == 0:
            c.drawString(x + 550, y, "All topics")
        else:
            c.drawString(x + 550, y, histogramTopic[0][0])
        y -= margin
        c.drawInlineImage(
            "histogram.png", page_width/2 - 1000,
            y - 1000, 2000, 1000
        )  # Drawing the histogram
        y -= margin

        c.save()  # Save the pdf file
        email = render_template(
            "emails/report_email.html", parentName=child[0][3],
            childName=child[0][0]
        )
        sendAttachmentEmail(
            child[0][2],
            "Child Progress Report ("+request.form["startDate"] +
            " - "+request.form["endDate"]+")",
            email,
            child[0][0]+"_"+child[0][1]+"_"+startDate+"_"+endDate+".pdf"
        )
        os.remove("histogram.png")  # Delete the histogram image locally
        os.remove(
            child[0][0]+"_"+child[0][1]+"_"+startDate+"_"+endDate+".pdf"
        )  # Delete the pdf file locally

        return jsonify({"success": "Report Sent!"})

    if len(results) != 0:
        return render_template(
            "reports.html", title="Reports", form=form,
            childName=results[0][1]+" "+results[0][2],
            histogramData=histogram, meanScores=meanScores,
            revisionList=revision
        )
    else:
        if len(children) != 0:
            with db.engine.connect() as conn:
                childName = conn.execute(
                    text("SELECT * FROM Child WHERE ChildID=:id"),
                    {"id": children[0][0]}
                ).fetchall()
        else:
            childName = [("", "(No", "Child)")]
        return render_template(
            "reports.html", title="Reports", form=form,
            childName=childName[0][1]+" "+childName[0][2],
            histogramData=histogram, meanScores=meanScores,
            revisionList=revision
        )
