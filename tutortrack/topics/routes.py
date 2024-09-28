from flask import (
    render_template, redirect, url_for, flash, request, Blueprint, jsonify
)
from flask_login import current_user
from sqlalchemy import text
from tutortrack import db
from tutortrack.models import login_required
from tutortrack.utils import getChildrenSelectList, getTopicSelectList
from tutortrack.topics.forms import CreateTopicForm, UpdateTopicForm
from tutortrack.topics.utils import (
    createTopic, getHierarchyChartData, getChangeParentTopicList, updateTopic,
    changeSubtopicLevels, deleteSubtopics, deleteTopic
)


topics = Blueprint(
    "topics", __name__, template_folder="templates", static_folder="static",
    static_url_path="/topics/static"
)


@topics.route("/create/topic", methods=["GET", "POST"])
@login_required(type="tutor")
def create_topic():
    form = CreateTopicForm()
    # Set the child select options
    children = getChildrenSelectList()
    form.child.choices = children
    if len(children) != 0:
        topicList = getTopicSelectList(children[0][0])
    else:
        topicList = []
    # Set the 'parent topic' select options
    form.parentTopic.choices = topicList
    if form.validate_on_submit():
        # If form valid and submitted
        createTopic(form)
        return redirect(url_for("topics.view_topics"))
    else:
        if request.method == "POST" and "ajax" in request.form:
            # If child selection is updated, update 'parent topic' options
            child = request.form["child"]
            topicList = getTopicSelectList(child)
            if len(topicList) != 0:
                return jsonify(topicList)
            else:
                # Return indicator that there are no topics that can be
                # a parent topic
                return jsonify({"error": "Error"})

    return render_template(
        "create_topic.html", title="Create Topic", form=form
    )


@topics.route("/view/topics", methods=["GET", "POST"])
@login_required(type="tutor")
def view_topics():
    form = CreateTopicForm()
    # Set the child select options
    children = getChildrenSelectList()
    form.child.choices = children
    if len(children) != 0:
        data = getHierarchyChartData(children[0][0])
    else:
        data = []
    if request.method == "POST":
        # If the child selection is updated, the hierarchy chart needs
        # to be updated
        child = request.form["child"]
        data = getHierarchyChartData(child)
        return jsonify({"data": data})

    return render_template(
        "view_topics.html", title="Topics", form=form, data=data
    )


@topics.route("/view/topic/<childID>/<topicName>", methods=["GET", "POST"])
@topics.route("/topic/<childID>/<topicName>", methods=["GET", "POST"])
@login_required(type="tutor")
def change_topic_details(childID, topicName):
    with db.engine.connect() as conn:
        tutorParentIDs = conn.execute(text(
            "SELECT Parent.TutorID, Parent.ParentID " +
            "FROM Parent, Child " +
            "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
        ),
            {"id": childID}
        ).fetchall()[0]
        # If user is the child's tutor or parent
        if (
            current_user.userID == tutorParentIDs[0] or
            current_user.userID == tutorParentIDs[1]
        ):
            # Get child details
            child = conn.execute(text(
                "SELECT Firstname, Surname FROM Child WHERE ChildID=:id"
            ),
                {"id": childID}
            ).fetchall()[0]
            # Get topic details to display in form
            topicID = conn.execute(
                text("SELECT TopicID FROM Topic WHERE Name=:name"),
                {"name": topicName}
            ).fetchall()
            if len(topicID) != 0:
                # If topic exists
                currentTopic = conn.execute(text(
                    "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
                    "ChildTopic.ParentTopicID " +
                    "FROM Topic, ChildTopic " +
                    "WHERE Topic.TopicID=ChildTopic.TopicID AND " +
                    "ChildTopic.ChildID=:cID AND ChildTopic.TopicID=:tID"
                ),
                    {"cID": childID, "tID": topicID[0][0]}
                ).fetchall()
                if len(currentTopic) != 0:
                    # If topic is already linked to child with childID
                    parentTopic = conn.execute(text(
                        "SELECT Topic.TopicID, Topic.Name " +
                        "FROM Topic, ChildTopic " +
                        "WHERE Topic.TopicID=ChildTopic.TopicID AND " +
                        "ChildTopic.TopicID=:tID AND ChildTopic.ChildID=:cID"
                    ),
                        {"tID": currentTopic[0][3], "cID": childID}
                    ).fetchall()
                    topicList = getChangeParentTopicList(
                        childID, topicID[0][0]
                    )
                    # If the topic's 'parent topic ID' is not 0 then it is
                    # a subtopic
                    if currentTopic[0][3] != 0:
                        # Set form fields
                        form = UpdateTopicForm(
                            type="subtopic", parentTopic=parentTopic[0][0]
                        )
                        form.parentTopic.choices = topicList
                    else:
                        # Set form fields
                        form = UpdateTopicForm(type="topic")
                        form.parentTopic.choices = topicList

                    if form.validate_on_submit():
                        # If form is valid and submitted
                        levelChange = 0
                        if form.type.data == "topic":
                            update = updateTopic(
                                form, childID, currentTopic[0][0], 0, 0,
                                currentTopic[0][1]
                            )
                            levelChange = 0 - currentTopic[0][2]
                        else:
                            parentTopic = conn.execute(text(
                                "SELECT Level " +
                                "FROM ChildTopic " +
                                "WHERE ChildTopic.TopicID=:tID AND " +
                                "ChildTopic.ChildID=:cID"
                            ),
                                {"tID": form.parentTopic.data, "cID": childID}
                            ).fetchall()
                            update = updateTopic(
                                form, childID, currentTopic[0][0],
                                parentTopic[0][0] + 1, form.parentTopic.data,
                                currentTopic[0][1]
                            )
                            levelChange = (
                                parentTopic[0][0] + 1 - currentTopic[0][2]
                            )
                        # Update the level of each topic in the
                        # current topic's subtree
                        changeSubtopicLevels(
                            childID, currentTopic, levelChange
                        )
                        return update
                    elif request.method == "GET":
                        # Fill form with current topic details
                        form.name.data = currentTopic[0][1]
                        form.parentTopic.choices = topicList
                    return render_template(
                        "change_topic_details.html",
                        title="Change Topic Details",
                        child=child, parentTopic=topicList, childID=childID,
                        topicName=topicName, form=form
                    )
            # If topic does not exist or is not linked to child, then user
            # will be redirected
            flash("That topic does not exist.", "danger")
            return redirect(url_for("topics.view_topics"))
        else:
            # If user is not the child's tutor or parent
            flash("You are not permitted to access this page.", "danger")
            return redirect(url_for("other.home"))


@topics.route("/delete/topic/<childID>/<topicName>")
@login_required(type="tutor")
def delete_topic(childID, topicName):
    with db.engine.connect() as conn:
        child = conn.execute(text(
            "SELECT Parent.TutorID " +
            "FROM Parent, Child " +
            "WHERE Parent.ParentID=Child.ParentID AND Child.ChildID=:id"
        ),
            {"id": childID}
        ).fetchall()[0]
        if current_user.userID == child[0]:
            topic = conn.execute(text(
                "SELECT Topic.TopicID, Topic.Name, ChildTopic.Level, " +
                "ChildTopic.ParentTopicID " +
                "FROM Topic, ChildTopic, Child " +
                "WHERE Name=:name AND Child.ChildID=ChildTopic.ChildID " +
                "AND Topic.TopicID=ChildTopic.TopicID"
            ),
                {"name": topicName}
            ).fetchall()
            deleteSubtopics(childID, topic)
            deleteTopic(childID, topic[0][0])
            flash("The topic has been successfully deleted.", "info")
            return redirect(url_for("topics.view_topics"))
        else:
            flash("You are not permitted to access this page.", "danger")
            return redirect(url_for("other.home"))
