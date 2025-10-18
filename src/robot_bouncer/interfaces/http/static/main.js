const nameElement = document.querySelector("#guest-name");
const introElement = document.querySelector("#guest-introduction");
const factsList = document.querySelector("#guest-facts");
const feedbackElement = document.querySelector("#feedback");
const allowButton = document.querySelector("#allow-button");
const denyButton = document.querySelector("#deny-button");
const nextButton = document.querySelector("#next-button");
const scoreCorrectElement = document.querySelector("#score-correct");
const scoreTotalElement = document.querySelector("#score-total");

let currentGuest = null;
const score = { correct: 0, total: 0 };

function setLoadingState() {
  nameElement.textContent = "Loading guest...";
  introElement.textContent = "";
  factsList.innerHTML = "";
  feedbackElement.textContent = "";
  toggleActionButtons(true);
  nextButton.hidden = true;
}

function toggleActionButtons(disabled) {
  allowButton.disabled = disabled;
  denyButton.disabled = disabled;
}

async function fetchGuest() {
  setLoadingState();
  try {
    const response = await fetch("/api/next-guest");
    if (!response.ok) {
      throw new Error(`Unable to load guest: ${response.statusText}`);
    }
    const guest = await response.json();
    currentGuest = guest;
    renderGuest(guest);
    toggleActionButtons(false);
  } catch (error) {
    feedbackElement.textContent = error.message;
  }
}

function renderGuest(guest) {
  nameElement.textContent = guest.name;
  introElement.textContent = guest.introduction;
  factsList.innerHTML = "";
  guest.facts.forEach((fact) => {
    const li = document.createElement("li");
    li.textContent = fact;
    factsList.appendChild(li);
  });
}

async function handleDecision(event) {
  const action = event.target.dataset.action;
  if (!action || !currentGuest) {
    return;
  }

  toggleActionButtons(true);
  feedbackElement.textContent = "Checking with the robot...";

  try {
    const response = await fetch("/api/authorize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        guest_id: currentGuest.guestId,
        action,
      }),
    });

    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      const message = detail?.detail ?? "The robot is unsure. Try again.";
      throw new Error(message);
    }

    const result = await response.json();
    score.total += 1;
    if (result.correct) {
      score.correct += 1;
    }

    scoreCorrectElement.textContent = score.correct;
    scoreTotalElement.textContent = score.total;
    feedbackElement.textContent = result.message;
    nextButton.hidden = false;
  } catch (error) {
    feedbackElement.textContent = error.message;
    toggleActionButtons(false);
  }
}

allowButton.addEventListener("click", handleDecision);
denyButton.addEventListener("click", handleDecision);
nextButton.addEventListener("click", () => {
  fetchGuest();
});

fetchGuest();
