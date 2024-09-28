from flask import (
    render_template, redirect, url_for, flash, request, Blueprint, jsonify
)
from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.models import login_required
from tutortrack.utils import (
    getChildrenSelectList, getTopicSelectList, tutorGetResults,
    parentGetResults, topicTreeLength
)
from tutortrack.results.forms import LogResultForm, UpdateResultForm
from tutortrack.results.utils import logResult, updateResult, getCoefficients
import datetime

results = Blueprint(
    "results", __name__, template_folder="templates", static_folder="static",
    static_url_path="/results/static"
)


@results.route("/log/result", methods=["GET", "POST"])
@login_required(type="tutor")
def log_result():
    form = LogResultForm()
    # Set the child select options
    children = getChildrenSelectList()
    form.child.choices = children
    if len(children) != 0:
        topicList = getTopicSelectList(children[0][0])
    else:
        topicList = []
    # Set the topic select options
    form.topic.choices = topicList

    if form.validate_on_submit():
        # If form valid and submitted
        logResult(form)
        return redirect(url_for("results.view_results"))
    else:
        if request.method == "POST" and "ajax" in request.form:
            # If child selection is changed, update topic select
            # options
            topicList = getTopicSelectList(request.form["child"])
            if len(topicList) != 0:
                # Return topic list if there are topics
                return jsonify(topicList)
            else:
                # If no topics, return error indicator
                return jsonify({"error": "Error"})

    return render_template("log_result.html", title="Log Result", form=form)


@results.route("/view/results", methods=["GET", "POST"])
@login_required()
def view_results():
    form = LogResultForm()
    # Set the child select options
    children = getChildrenSelectList()
    form.child.choices = children
    if len(children) != 0:
        if current_user.type == "tutor":
            # Get all results for default child selection
            results = tutorGetResults(children[0][0], "0", None, None)
        elif current_user.type == "parent":
            # Get all results for default child selection
            results = parentGetResults(children[0][0], "0", None, None)
        topicList = getTopicSelectList(children[0][0], True)
    else:
        results = []
        topicList = []
    # Set the topic select options
    form.topic.choices = topicList

    if request.method == "POST":
        if "childChange" in request.form:
            # When child selection is changed
            topicID = "0"
        elif "topicChange" in request.form:
            # When topic selection is changed
            topicID = request.form["topic"]

        # Get results for selected child
        if current_user.type == "tutor":
            results = tutorGetResults(
                request.form["child"], topicID, None, None
            )
        elif current_user.type == "parent":
            results = parentGetResults(
                request.form["child"], topicID, None, None
            )

        if "childChange" in request.form:
            # Get topics for the particular child
            topicList = getTopicSelectList(request.form["child"], True)
            # Return the template to be rendered in the 'results' divider
            # and the new list of topics
            return jsonify({
                "results": render_template(
                    "view_child_results.html", title="Results",
                    results=results, form=form
                ),
                "topics": topicList
            })
        elif "topicChange" in request.form:
            # Return template of new results
            return render_template(
                "view_child_results.html", title="Results",
                results=results, form=form
            )

    return render_template(
        "view_results.html", title="Results", results=results, form=form
    )


@results.route("/result/<childID>/<resultID>", methods=["GET", "POST"])
@login_required()
def result_details(childID, resultID):
    with db.engine.connect() as conn:
        if current_user.type == "tutor":
            child = conn.execute(text(
                "SELECT User.UserID, Child.ChildID, Child.Firstname, " +
                "Child.Surname " +
                "FROM User, Parent, Child " +
                "WHERE User.UserID=Parent.TutorID AND Parent.ParentID=" +
                "Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()[0]
        elif current_user.type == "parent":
            child = conn.execute(text(
                "SELECT Parent.ParentID, Child.ChildID, Child.Firstname, " +
                "Child.Surname " +
                "FROM Parent, Child " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()[0]

        if child[0] != current_user.userID:
            # If child is not linked to user
            flash("You are not permitted to access this page.", "danger")
            return redirect(url_for("other.home"))

        result = conn.execute(
            text("SELECT * FROM Result WHERE ResultID=:rID AND ChildID=:cID"),
            {"rID": resultID, "cID": childID}
        ).fetchall()[0]
        topic = conn.execute(
            text("SELECT Name FROM Topic WHERE TopicID=:id"),
            {"id": result[7]}
        ).fetchall()

        return render_template(
            "result_details.html", title="Result Details", child=child,
            result=result, topic=topic
        )


@results.route(
    "/change/result/details/<childID>/<resultID>", methods=["GET", "POST"]
)
@login_required(type="tutor")
def change_result_details(childID, resultID):
    children = getChildrenSelectList()
    # Get topics for child
    topicList = getTopicSelectList(childID)

    with db.engine.connect() as conn:
        tutorParentIDs = conn.execute(text(
            "SELECT Parent.TutorID, Parent.ParentID " +
            "FROM Parent, Child " +
            "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
        ),
            {"id": childID}
        ).fetchall()[0]

    if (
        current_user.userID == tutorParentIDs[0] or
        current_user.userID == tutorParentIDs[1]
    ):
        # If user is child's tutor or parent
        with db.engine.connect() as conn:
            # Get result details to display in form
            currentResult = conn.execute(
                text("SELECT * FROM Result WHERE ResultID=:id"),
                {"id": resultID}
            ).fetchall()[0]
        # Set child and topic selections within form
        form = UpdateResultForm(child=childID, topic=currentResult[7])
        if form.validate_on_submit():
            # If form valid and submitted
            update = updateResult(form, resultID)
            return update
        elif request.method == "GET":
            # Fill form with current details of result
            form.child.choices = children
            form.topic.choices = topicList
            form.date.data = datetime.datetime.strptime(
                currentResult[0][1], "%Y-%m-%d"
            )
            form.type.data = currentResult[2]
            form.studentMark.data = currentResult[3]
            form.totalMark.data = currentResult[4]
        else:
            form.child.choices = children
            form.topic.choices = topicList
            # If child selection is changed, update topic list
            if request.method == "POST" and "ajax" in request.form:
                topicList = getTopicSelectList(request.form["child"])
                if len(topicList) != 0:
                    # Return topic list if there are topics
                    return jsonify(topicList)
                else:
                    # If no topics, return error indicator
                    return jsonify({"error": "Error"})

        return render_template(
            "change_result_details.html", title="Change Result Details",
            form=form, resultID=currentResult[0], childID=childID
        )
    else:
        # If user isn't child's tutor or parent
        flash("You are not permitted to access this page.", "danger")
        return redirect(url_for("other.home"))


@results.route("/delete/result/<childID>/<resultID>")
@login_required(type="tutor")
def delete_result(childID, resultID):
    with db.engine.connect() as conn:
        with conn.begin():
            tutorParentIDs = conn.execute(text(
                "SELECT Parent.TutorID, Parent.ParentID " +
                "FROM Parent, Child " +
                "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()[0]
            if (
                current_user.userID == tutorParentIDs[0] or
                current_user.userID == tutorParentIDs[1]
            ):
                conn.execute(
                    text("DELETE FROM Result WHERE ResultID=:id"),
                    {"id": resultID}
                )
                flash("The result has been successfully deleted.", "info")
                return redirect(url_for("results.view_results"))
            else:
                flash("You are not permitted to access this page.", "danger")
                return redirect(url_for("other.home"))


@results.route("/results/scatter/graph", methods=["GET", "POST"])
@login_required()
def scatter_graph():
    form = LogResultForm()
    children = getChildrenSelectList()
    form.child.choices = children

    if len(children) != 0:
        # Get the topics for the default child selection
        topicList = getTopicSelectList(children[0][0])
        # Get results for topic and subtopics
        if len(topicList) != 0:
            if current_user.type == "tutor":
                results = tutorGetResults(
                    children[0][0], topicList[0][0], None, None
                )[::-1]
            elif current_user.type == "parent":
                results = parentGetResults(
                    children[0][0], topicList[0][0], None, None
                )[::-1]
            numTopics = topicTreeLength(children[0][0], topicList[0][0])
        else:
            results = []
            numTopics = 0
    else:
        topicList = []
        results = []
        numTopics = 0

    form.topic.choices = topicList

    if len(results) > 1:
        coefficients = getCoefficients(results)
    else:
        coefficients = (0, 0)

    if request.method == "POST":
        if "childChange" in request.form:
            # If child selection is changed, get topics for child
            topicList = getTopicSelectList(request.form["child"])
            # Get results for topic and subtopics for selected child
            if len(topicList) != 0:
                if current_user.type == "tutor":
                    results = tutorGetResults(
                        request.form["child"], topicList[0][0], None, None
                    )[::-1]
                elif current_user.type == "parent":
                    results = parentGetResults(
                        request.form["child"], topicList[0][0], None, None
                    )[::-1]
                numTopics = topicTreeLength(
                    request.form["child"], topicList[0][0]
                )
            else:
                results = []
                numTopics = 0
        elif "topicChange" in request.form:
            # If topic selection is changed
            if current_user.type == "tutor":
                results = tutorGetResults(
                    request.form["child"], request.form["topic"], None, None
                )[::-1]
            elif current_user.type == "parent":
                results = parentGetResults(
                    request.form["child"], request.form["topic"], None, None
                )[::-1]
            numTopics = topicTreeLength(
                request.form["child"], request.form["topic"]
            )

        if len(results) > 1:
            coefficients = getCoefficients(results)
        else:
            coefficients = (0, 0)

        if "childChange" in request.form:
            return jsonify({
                "results": results, "topics": topicList,
                "coefficients": coefficients, "topicLength": numTopics
            })
        elif "topicChange" in request.form:
            return jsonify({
                "results": results, "coefficients": coefficients,
                "topicLength": numTopics
            })

    return render_template(
        "scatter_graph.html", title="Results", form=form, results=results,
        a=coefficients[0], b=coefficients[1], topicLength=numTopics
    )
