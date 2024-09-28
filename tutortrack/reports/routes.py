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
    form = ReportForm()
    # Set child selection choices
    children = getChildrenSelectList()
    form.child.choices = children
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

    if request.method == "POST":
        if "childChange" in request.form:
            # When child selection is changed
            topicID = "0"
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
        elif "topicChange" in request.form:
            # When topic selection is changed
            topicID = request.form["topic"]
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]
        elif "dateChange" in request.form:
            # When date range is changed
            topicID = request.form["topic"]
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
                # A ValueError will be thrown if the text entered
                # cannot be converted to a datetime object
                return jsonify({"error": "notDates"})
        elif "sendReport" in request.form:
            # When 'Send Report' is pressed
            with db.engine.connect() as conn:
                # Get child and parent details
                child = conn.execute(text(
                    "SELECT Child.Firstname, Child.Surname, User.Email, " +
                    "User.Firstname " +
                    "FROM Child, User " +
                    "WHERE ChildID=:cID AND User.UserID=Child.ParentID"
                ),
                    {"cID": request.form["child"]}
                ).fetchall()[0]
                # Get selected topic details
                histogramTopic = conn.execute(text(
                    "SELECT Name, ParentTopicID " +
                    "FROM Topic, ChildTopic " +
                    "WHERE Topic.TopicID=:tID AND Topic.TopicID=" +
                    "ChildTopic.TopicID AND ChildTopic.ChildID=:cID"
                ),
                    {"tID": request.form["topic"],
                        "cID": request.form["child"]}
                ).fetchall()

        # Get results based on selection
        results = tutorGetResults(
            request.form["child"], topicID, startDate, endDate
        )
        # Get data list for histogram
        histogram = getHistogramData(results)

        if "topicChange" in request.form:
            return jsonify({"histogramData": histogram})

        # Get child topics
        topicList = getTopicSelectList(request.form["child"], True)
        # Get mean score for each topic
        meanScores = getMeans(
            request.form["child"], topicList, startDate, endDate
        )
        # Get revision list
        revision = createRevisionList(
            request.form["child"], meanScores, startDate, endDate
        )

        if "childChange" in request.form:
            if len(results) != 0:
                childName = results[0][1]+" "+results[0][2]
            else:
                with db.engine.connect() as conn:
                    # If no results for child
                    child = conn.execute(
                        text("SELECT * FROM Child WHERE ChildID=:id"),
                        {"id": request.form["child"]}
                    ).fetchall()[0]
                    childName = child[1]+" "+child[2]
            return jsonify({
                "topics": topicList,
                "childName": childName,
                "histogramData": histogram,
                "topicBreakdown": render_template(
                    "topic_breakdown.html", meanScores=meanScores,
                    revisionList=revision)
            })
        elif "dateChange" in request.form:
            return jsonify({
                "histogramData": histogram,
                "topicBreakdown": render_template(
                    "topic_breakdown.html", meanScores=meanScores,
                    revisionList=revision
                )
            })
        elif "sendReport" in request.form:
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

            startDateText = startDate.replace("/", "")
            endDateText = endDate.replace("/", "")

            # Register the font for the canvas
            pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))

            # Page information
            pageWidth = 2156
            pageHeight = (
                600 + 80*len(meanScores) + 170 + 80*len(revision) + 1400
            )
            margin = 100

            # Create and name the .pdf file
            c = canvas.Canvas(
                child[0]+"_"+child[1]+"_"+startDateText+"_"+endDateText+".pdf"
            )
            c.setPageSize((pageWidth, pageHeight))

            # Title
            c.setFont("Arial", 80)
            title = "Progress Report"
            titleWidth = stringWidth(title, "Arial", 80)
            c.drawString(
                (pageWidth-titleWidth)/2, pageHeight - margin*2, title
            )
            y = pageHeight - margin*3.5
            x = 2*margin

            # Report details
            c.setFont("Arial", 50)
            c.drawString(x, y, "Child Name:")
            c.setFont("Arial", 45)
            c.drawString(x + 550, y, child[0]+" "+child[1])
            y -= margin*0.8

            c.setFont("Arial", 50)
            c.drawString(x, y, "Date Range:")
            c.setFont("Arial", 45)
            c.drawString(
                x + 550, y, startDate + " - " + endDate
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
                "histogram.png", pageWidth/2 - 1000,
                y - 1000, 2000, 1000
            )  # Drawing the histogram
            y -= margin

            c.save()  # Save the pdf file
            email = render_template(
                "emails/report_email.html", parentName=child[3],
                childName=child[0]
            )
            sendAttachmentEmail(
                child[2],
                f"Child Progress Report ({startDate} - {endDate})",
                email,
                child[0]+"_"+child[1]+"_"+startDateText+"_"+endDateText+".pdf"
            )
            os.remove("histogram.png")  # Delete the histogram image locally
            os.remove(
                child[0]+"_"+child[1]+"_"+startDateText+"_"+endDateText+".pdf"
            )  # Delete the pdf file locally

            return jsonify({"success": "Report Sent!"})

    if len(results) != 0:
        childName = results[0][1]+" "+results[0][2]
    else:
        if len(children) != 0:
            with db.engine.connect() as conn:
                child = conn.execute(
                    text("SELECT * FROM Child WHERE ChildID=:id"),
                    {"id": children[0][0]}
                ).fetchall()[0]
                childName = child[1]+" "+child[2]
        else:
            childName = "No Child"
    return render_template(
        "reports.html", title="Reports", form=form,
        childName=childName, histogramData=histogram,
        meanScores=meanScores, revisionList=revision
    )
