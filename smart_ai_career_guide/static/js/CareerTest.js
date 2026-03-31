let currentStep = 0;
let steps;

window.onload = function () {
    steps = document.querySelectorAll(".step");
    showStep();
};

function showStep() {

    steps.forEach((step, index) => {
        step.style.display = (index === currentStep) ? "block" : "none";
    });

    let titles = [
        "Step 1: Academic Data",
        "Step 2: Interests",
        "Step 3: Lifestyle",
        "Step 4: Skills"
    ];

    document.getElementById("step-title").innerText = titles[currentStep];

    let progress = ((currentStep + 1) / steps.length) * 100;
    document.getElementById("progress").style.width = progress + "%";

    let btn = document.getElementById("nextBtn");

    if (currentStep === steps.length - 1) {
        btn.innerText = "Submit 🚀";
    } else {
        btn.innerText = "Next ➡";
    }
}

function nextStep() {
    if (currentStep < steps.length - 1) {
        currentStep++;
        showStep();
    } else {
        document.getElementById("careerForm").submit();
    }
}

function prevStep() {
    if (currentStep > 0) {
        currentStep--;
        showStep();
    }
}

function selectInterest(value) {
    document.getElementById("interest").value = value;

    let buttons = document.querySelectorAll(".interest-options button");

    buttons.forEach(btn => {
        btn.style.background = "#f3f4f6";
        btn.style.color = "#111";
    });

    event.target.style.background = "#7c3aed";
    event.target.style.color = "white";
}