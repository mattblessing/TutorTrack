from flask import render_template, redirect, url_for, flash
from sqlalchemy import text
from tutortrack import db
from tutortrack.utils import notificationEmail
import random


def logResult(form):
    """
    Add a submitted result to the database.

    Args:
        form: The result form filled out by a tutor.
    """
    if form.topic.data == None:
        flash("You cannot log a result with no topic.", "danger")
    else:
        with db.engine.connect() as conn:
            with conn.begin():
                # Get parent email address
                parent = conn.execute(text(
                    "SELECT Email " +
                    "FROM User, Child " +
                    "WHERE Child.ParentID=User.UserID AND Child.ChildID=:id"
                ),
                    {"id": form.child.data}
                ).fetchall()

                percentage = round(
                    (form.studentMark.data / form.totalMark.data) * 100, 1
                )
                # See if result already exists in database
                result = conn.execute(text(
                    "SELECT * " +
                    "FROM Result " +
                    "WHERE Date=:date AND Type=:type AND StudentMark=:sm " +
                    "AND TotalMark=:tm AND Percentage=:pc AND ChildID=:cID " +
                    "AND TopicID=:tID"
                ),
                    {
                        "date": form.date.data, "type": form.type.data,
                        "sm": form.studentMark.data,
                        "tm": form.totalMark.data,
                        "pc": percentage, "cID": form.child.data,
                        "tID": form.topic.data
                }
                ).fetchall()

                if len(result) == 0:
                    # If it doesn't
                    resultID = generateResultID()
                    conn.execute(text(
                        "INSERT INTO Result VALUES " +
                        "(:id, :date, :type, :sm, :tm, :pc, :cID, :tID)"
                    ),
                        {
                            "id": resultID, "date": form.date.data,
                            "type": form.type.data,
                            "sm": form.studentMark.data,
                            "tm": form.totalMark.data, "pc": percentage,
                            "cID": form.child.data, "tID": form.topic.data
                    }
                    )
                    email = render_template("emails/result_logged.html")
                    notificationEmail(parent[0][0], email)
                    flash("The result was successfully logged.", "success")
                else:
                    # If it does, do not add to database
                    flash("That result already exists", "danger")


def generateResultID():
    """
    Generate a unique ID for a new result.
    """
    unique = False
    while unique == False:
        id = random.randint(100000, 999999)
        with db.engine.connect() as conn:
            idSearch = conn.execute(
                text("SELECT * FROM Result WHERE ResultID=:id"), {"id": id}
            ).fetchall()
        if len(idSearch) == 0:
            unique = True
    return id


def updateResult(form, resultID):
    """
    Update the details of a particular result.

    Args:
        form: The updated result form filled out by a tutor.
        resultID (str): The existing result's ID.
    """
    with db.engine.connect() as conn:
        with conn.begin():
            # Get parent email address
            parent = conn.execute(text(
                "SELECT Email " +
                "FROM User, Child " +
                "WHERE Child.ParentID=User.UserID AND Child.ChildID=:id"
            ),
                {"id": form.child.data}
            ).fetchall()
            percentage = round(
                (form.studentMark.data / form.totalMark.data) * 100, 1
            )

            # See if result already exists in table
            result = conn.execute(text(
                "SELECT * " +
                "FROM Result " +
                "WHERE Date=:date AND Type=:type AND StudentMark=:sm AND " +
                "TotalMark=:tm AND Percentage=:pc AND ChildID=:cID AND " +
                "TopicID=:tID"
            ),
                {
                    "date": form.date.data, "type": form.type.data,
                    "sm": form.studentMark.data, "tm": form.totalMark.data,
                    "pc": percentage, "cID": form.child.data,
                    "tID": form.topic.data
            }
            ).fetchall()

            if len(result) == 0 or str(result[0][0]) == str(resultID):
                # If it doesn't
                conn.execute(text(
                    "UPDATE RESULT SET Date=:date, Type=:type, " +
                    "StudentMark=:sm, TotalMark=:tm, " +
                    "Percentage=:pc, ChildID=:cID, TopicID=:tID " +
                    "WHERE ResultID=:rID"
                ),
                    {
                        "date": form.date.data, "type": form.type.data,
                        "sm": form.studentMark.data,
                        "tm": form.totalMark.data,
                        "pc": percentage, "cID": form.child.data,
                        "tID": form.topic.data, "rID": resultID
                }
                )
                email = render_template("emails/result_updated.html")
                # Send notification to parent
                notificationEmail(parent[0][0], email)
                flash(
                    "The result details were successfully changed.", "success"
                )
            else:
                # If it does
                flash(
                    "That result already exists for the selected child.",
                    "danger"
                )

        return redirect(url_for("results.view_results"))


def estimateCoefficients(x, y):
    """
    Given ordered lists of the x and y values in a scatter plot,
    estimate the coefficients of a line of best fit.

    Args:
        x (list): The x values.
        y (list): The y values.

    Returns:
        a (float): The intercept.
        b (float): The gradient.
    """
    xTotal = 0
    yTotal = 0
    sumOfXY = 0
    sumOfXX = 0
    n = len(x)  # Number of points
    for i in range(n):
        xTotal += x[i]
    mx = xTotal/n  # Mean x value
    for i in range(n):
        yTotal += y[i]
    my = yTotal/n  # Mean y value
    for i in range(n):
        sumOfXY += x[i]*y[i]
    for i in range(n):
        sumOfXX += x[i]**2
    Sxy = sumOfXY - n * mx * my
    Sxx = sumOfXX - n * mx * mx
    if Sxx != 0:
        b = Sxy / Sxx
        a = my - b * mx
    else:
        b = 0
        a = 0
    return (a, b)


def getCoefficients(results):
    """
    Get the coefficients for the scatter graph line of best fit.

    Args:
        results (list): A list of result records in the scatter graph.

    Returns:
        coefficients (tuple): The coefficients.
    """
    x = []
    y = []
    for i in range(len(results)):
        x.append(float(i+1))
        y.append(float(results[i][6]))
    coefficients = estimateCoefficients(x, y)
    return coefficients
