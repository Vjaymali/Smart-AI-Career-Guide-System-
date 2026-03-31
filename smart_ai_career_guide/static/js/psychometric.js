const questions = [
  { q: "I enjoy solving logical problems.", type: "technical" },
  { q: "I like designing or creating new things.", type: "creative" },
  { q: "I enjoy helping people solve their problems.", type: "social" },
  { q: "I like taking leadership and managing tasks.", type: "business" },
  { q: "I am interested in coding or technology.", type: "technical" },
  { q: "I enjoy drawing, writing, or content creation.", type: "creative" },
  { q: "I communicate well with others.", type: "social" },
  { q: "I like business ideas and startups.", type: "business" },
  { q: "I enjoy mathematics and analysis.", type: "technical" },
  { q: "I think creatively to solve problems.", type: "creative" },
  { q: "I like teamwork and collaboration.", type: "social" },
  { q: "I take initiative in projects.", type: "business" },
  { q: "I enjoy working with computers.", type: "technical" },
  { q: "I like visual storytelling.", type: "creative" },
  { q: "I understand others' emotions easily.", type: "social" },
  { q: "I like planning and organizing.", type: "business" },
  { q: "I enjoy learning new technologies.", type: "technical" },
  { q: "I have a strong imagination.", type: "creative" },
  { q: "I enjoy public speaking.", type: "social" },
  { q: "I am confident taking risks.", type: "business" },
  { q: "I like problem-solving challenges.", type: "technical" },
  { q: "I enjoy creative thinking tasks.", type: "creative" },
  { q: "I help others when they need support.", type: "social" },
  { q: "I like decision making.", type: "business" },
  { q: "I enjoy analytical thinking.", type: "technical" }
];

let current = 0;
let answers = new Array(questions.length).fill(null);

function loadQuestion() {

    document.getElementById("question-box").innerText = questions[current].q;

    document.getElementById("q-number").innerText =
        `Question ${current + 1} of ${questions.length}`;

    let progress = ((current) / questions.length) * 100;
    document.getElementById("progress").style.width = progress + "%";

    // ✅ RESET ALL BUTTONS (IMPORTANT FIX)
    let buttons = document.querySelectorAll(".options button");

    buttons.forEach(btn => {
        btn.style.background = "#f3f4f6";
        btn.style.color = "#111";
    });

    // ✅ IF ANSWER ALREADY SELECTED (for previous navigation)
    if (answers[current] !== null) {
        buttons[answers[current] - 1].style.background = "#7c3aed";
        buttons[answers[current] - 1].style.color = "white";
    }

    // ✅ UPDATE NEXT BUTTON TEXT
    let nextBtn = document.getElementById("nextBtn");

    if (current === questions.length - 1) {
        nextBtn.innerText = "Submit 🚀";
    } else {
        nextBtn.innerText = "Next ➡";
    }
}
    // Reset button styles 
    { 
        let buttons = document.querySelectorAll(".options button");
        buttons.forEach(btn => {
        btn.style.background = "#f3f4f6";
        btn.style.color = "#111";   // 🔥 IMPORTANT
    });

    // Highlight selected
    if (answers[current] !== null) {
        buttons[answers[current] - 1].style.background = "white";
        buttons[answers[current] - 1].style.color = "#7c3aed";
    }
}

function selectAnswer(value) {
    answers[current] = value;

    let buttons = document.querySelectorAll(".options button");

    buttons.forEach(btn => {
        btn.style.background = "#f3f4f6";
        btn.style.color = "#111";
    });

    buttons[value - 1].style.background = "#7c3aed";
    buttons[value - 1].style.color = "white";
}

function nextQuestion() {

    if (answers[current] === null) {
        alert("Please select an option!");
        return;
    }

    if (current < questions.length - 1) {
        current++;
        loadQuestion();
    } else {
        submitTest();   // ✅ FINAL SUBMIT
    }
}
function prevQuestion() {
    if (current > 0) {
        current--;
        loadQuestion();
    }
}

function submitTest() {

    let finalAnswers = [];

    for (let i = 0; i < questions.length; i++) {
        finalAnswers.push({
            type: questions[i].type,
            score: answers[i]
        });
    }

    fetch("/submit-psychometric", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({answers: finalAnswers})
    })
    .then(res => res.json())
    .then(data => {
        window.location.href = "/career-test";
    });
}

window.onload = function() {
    loadQuestion();
};