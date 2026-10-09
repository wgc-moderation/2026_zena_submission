// Default timer is a 25 minute focus session
let startingTime = 25 * 60;
let timeLeft = startingTime;

// Keeps track of the timer that is currently running
let intervalId = null;

// Stores which type of timer is currently selected
let currentMode = "focus";

// Counts how many focus sessions have been finished
let completedSessions = 0;


// Updates the time displayed on the website
function updateDisplay() {
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  document.getElementById("timer-display").textContent =
    `${minutes}:${seconds.toString().padStart(2, "0")}`;
}


// Starts the countdown
function startTimer() {

  // Stops another timer being created if one is already running
  if (intervalId !== null) {
    return;
  }

  // Changes the message depending on the selected mode
  if (currentMode === "focus") {
    document.getElementById("timer-message").textContent = "Focus time";
  } else {
    document.getElementById("timer-message").textContent = "Break time";
  }

  // Runs the countdown once every second
  intervalId = setInterval(function () {

    if (timeLeft > 0) {
      timeLeft--;
      updateDisplay();
    }

    // Stops the timer when it reaches zero
    if (timeLeft === 0) {
      clearInterval(intervalId);
      intervalId = null;

      document.getElementById("timer-message").textContent =
        "Session complete!";

      // Only completed focus sessions are counted
      if (currentMode === "focus") {
        completedSessions++;

        document.getElementById("session-count").textContent =
          completedSessions;
      }
    }

  }, 1000);
}


// Pauses the timer without changing the time left
function pauseTimer() {
  clearInterval(intervalId);
  intervalId = null;

  document.getElementById("timer-message").textContent =
    "Timer paused";
}


// Returns the timer to the beginning of the selected mode
function resetTimer() {
  clearInterval(intervalId);
  intervalId = null;

  timeLeft = startingTime;

  updateDisplay();

  document.getElementById("timer-message").textContent =
    "Timer reset";
}


// Changes between focus, short break and long break
function setTimerMode(mode) {
  clearInterval(intervalId);
  intervalId = null;

  currentMode = mode;

  // 25 minute focus timer
  if (mode === "focus") {
    startingTime = 25 * 60;

    document.getElementById("mode-title").textContent =
      "Focus";

    document.getElementById("timer-message").textContent =
      "Focus session ready";
  }

  // 5 minute short break
  else if (mode === "short") {
    startingTime = 5 * 60;

    document.getElementById("mode-title").textContent =
      "Short Break";

    document.getElementById("timer-message").textContent =
      "Take a quick break";
  }

  // 15 minute long break
  else if (mode === "long") {
    startingTime = 15 * 60;

    document.getElementById("mode-title").textContent =
      "Long Break";

    document.getElementById("timer-message").textContent =
      "Time for a longer break";
  }

  // Resets the countdown to the newly selected time
  timeLeft = startingTime;

  updateActiveButton(mode);
  updateDisplay();
}


// Creates a timer using the number of minutes entered by the user
function setCustomTimer() {
  const customMinutes =
    parseInt(document.getElementById("custom-minutes").value);

  // Makes sure the entered time is valid
  if (isNaN(customMinutes) || customMinutes < 1 || customMinutes > 180) {
    document.getElementById("timer-message").textContent =
      "Enter a time between 1 and 180 minutes";

    return;
  }

  // Stops the old timer before setting the custom one
  clearInterval(intervalId);
  intervalId = null;

  currentMode = "focus";
  startingTime = customMinutes * 60;
  timeLeft = startingTime;

  document.getElementById("mode-title").textContent =
    "Custom Focus";

  document.getElementById("timer-message").textContent =
    `${customMinutes} minute session ready`;

  updateActiveButton("custom");
  updateDisplay();
}


// Changes the button styling to show the selected mode
function updateActiveButton(mode) {
  const buttons = document.querySelectorAll(".timer-mode");

  // Removes the selected style from each preset button
  buttons.forEach(function (button) {
    button.classList.remove("active-timer-mode");
  });

  // Adds the selected style to the correct button
  if (mode === "focus") {
    document
      .getElementById("focus-button")
      .classList.add("active-timer-mode");
  }

  else if (mode === "short") {
    document
      .getElementById("short-button")
      .classList.add("active-timer-mode");
  }

  else if (mode === "long") {
    document
      .getElementById("long-button")
      .classList.add("active-timer-mode");
  }
}


// Displays the starting time when the page first opens
updateDisplay();