from flask import Flask, request, render_template, redirect, flash
from flask import session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


# ROOT ROUTE which displays the title and instruction of the survey, and a button to start the survey
@app.route('/')
def survey_start_page():
    """ The start page of survey which render the "survey_start.html" page  """

    return render_template("survey_start.html", survey = survey)

# When we click on "start survey" button the page gets redirected to "/questions/0" which displays the survey questions
@app.route('/begin', methods= ['POST'])
def begin_survey():
    """ Redirects it to "/questions/0" Route """

    # Making a empty list session of "responses" and also to Clear the session of responses.
    session["responses"] = []

    return redirect("/questions/0")

# Survey Question Route
@app.route("/questions/<int:id>")
def survey_question(id):
    """ Renders the "question_survey.html" page to display the particular question based on the id we get from the route """

    # Getting the response LIST from the session
    responses = session.get("responses")

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    # Checking whether the user is answering questions next by next rather than jumping between questions or trying to enter a URL that doesn't match the question "id" in the route
    if len(responses) != id:
        # redirecting to correct next question page 
        flash(f"Invalid question id: {id}.")
        return redirect(f"/questions/{len(responses)}")


    return render_template("question_survey.html", question = survey.questions[id])

# When user submits the answer, the page has to be redirected to the next survey question
@app.route("/answer", methods = ["POST"])
def handle_answers():
    """ Save the responses and redirect to next question """

    choice = request.form['answer']

    # appending the choice to responses list into the session
    responses = session.get("responses")
    responses.append(choice)
    session["responses"] = responses


    # If all survey questions are responded the redirect to "/complete" Route
    if len(responses) == len(survey.questions):
        return redirect('/complete')

    return redirect(f"/questions/{len(responses)}")

# Thank the user route
@app.route("/complete")
def thank_user():
    """Survey complete. Show completion page."""

    return render_template("complete.html")
