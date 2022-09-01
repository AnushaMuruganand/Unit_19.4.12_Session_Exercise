from flask import Flask, request, render_template, redirect, flash
from flask import session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

# ROOT ROUTE to pick the survey

@app.route("/")
def show_pick_survey_form():
    """Show pick-a-survey form."""

    return render_template("pick-survey.html", surveys=surveys)

# ROOT ROUTE which displays the title and instruction of the survey user picked, and a button to start the survey
@app.route('/', methods = ["POST"])
def survey_start_page():
    """ The start page of survey which render the "survey_start.html" page  """

    survey_code = request.form['survey_code']

    # Getting the survey LIST based on the survey_code
    survey = surveys[survey_code]

    # Storing the survey picked into a session
    session["current-survey"] = survey_code

    # Checking if user has already complted this survey with the help of cookie we created in "/complete" ROUTE.
    # If so, don't let them re-take a survey until cookie times out
    if request.cookies.get(f"completed_{survey_code}"):
        return render_template("already-done.html")

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

    # Getting the survey_code user selected from the session
    survey_code = session['current-survey']
    survey = surveys[survey_code]

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
    text = request.form.get('text',"")

    # appending the choice to responses list into the session
    responses = session.get("responses")
    responses.append({"choice": choice, "text": text})
    session["responses"] = responses

    # Getting the survey_code user selected from the session
    survey_code = session['current-survey']
    survey = surveys[survey_code]


    # If all survey questions are responded the redirect to "/complete" Route
    if len(responses) == len(survey.questions):
        return redirect('/complete')

    return redirect(f"/questions/{len(responses)}")

# Thank the user route
@app.route("/complete")
def thank_user():
    """Survey complete. Show completion page."""

    # Getting the survey_code user selected from the session
    survey_code = session['current-survey']
    survey = surveys[survey_code]

    # Getting the response LIST from the session
    responses = session["responses"]

    html = render_template("complete.html", survey = survey, responses = responses)

    # Set cookie noting this survey is done so they can't re-do it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_code}", "yes", max_age = 60)
    return response
