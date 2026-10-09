from flask import Flask, render_template, request, abort

from data import STATS, INFO_PAGES, FACT_TABS, QUIZ, QUIZ_VERDICTS
from calc import calculate, DIET_NAMES

app = Flask(__name__)


# Меню для всех страниц: добавляем его автоматически в каждый шаблон
@app.context_processor
def inject_menu():
    return {"menu_info": INFO_PAGES}


@app.route("/")
def index():
    return render_template("main.html", stats=STATS)


@app.route("/info/<slug>")
def info(slug):
    page = INFO_PAGES.get(slug)
    if page is None:
        abort(404)
    return render_template("info.html", page=page, slug=slug)


@app.route("/facts")
@app.route("/facts/<slug>")
def facts(slug=None):
    if slug is None:
        slug = next(iter(FACT_TABS))  # первая вкладка по умолчанию
    if slug not in FACT_TABS:
        abort(404)
    return render_template(
        "facts.html",
        tabs=FACT_TABS,
        active=slug,
        tab=FACT_TABS[slug],
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        results = []
        score = 0
        for number, question in enumerate(QUIZ):
            answer = request.form.get(f"q{number}")
            chosen = (
                int(answer) if answer is not None and answer.isdigit() else None
            )
            is_correct = chosen == question["correct"]
            score += is_correct
            results.append({"chosen": chosen, "is_correct": is_correct})

        verdict = next(v for v in QUIZ_VERDICTS if score >= v[0])
        return render_template(
            "quiz.html", quiz=QUIZ, results=results,
            score=score, total=len(QUIZ), verdict=verdict,
        )
    return render_template("quiz.html", quiz=QUIZ, results=None)


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        result = calculate(request.form)
    return render_template("calculator.html", result=result, diets=DIET_NAMES)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
