// Get the remaining timer value from the session in seconds
let remainingTime = window.remainingTime || 0;
let timerElement = document.getElementById('countdown-timer');

function updateTimer() {
  // Calculate the remaining minutes and seconds (integers only)
  const minutes = Math.floor(remainingTime / 60);
  const seconds = Math.floor(remainingTime % 60);

  // Display in the format "minutes and seconds"
  timerElement.innerText = `${minutes} minute${minutes !== 1 ? 's' : ''} and ${seconds} second${seconds !== 1 ? 's' : ''}`;

  // If time has expired
  if (remainingTime <= 0) {
    timerElement.innerText = "Expired";
    setTimeout(() => {
      window.location.href = '/';
    }, 1000);
    return;
  }

  remainingTime--;
  setTimeout(updateTimer, 1000);
}

updateTimer();

// Fortschrittsbalken (visueller Timer)
(function () {
  const totalTime = 300; // 5 Minuten in Sekunden
  let timeLeft = window.remainingTime || 0;
  const bar = document.getElementById("progress-bar");

  function updateProgressBar() {
    if (!bar || timeLeft < 0) return;

    const percent = (timeLeft / totalTime) * 100;
    bar.style.width = percent + "%";

    // Farbverlauf: grün > orange > rot
    if (percent > 66) {
      bar.style.backgroundColor = "#4caf50"; // grün
    } else if (percent > 33) {
      bar.style.backgroundColor = "#ff9800"; // orange
    } else {
      bar.style.backgroundColor = "#f44336"; // rot
    }

    timeLeft--;
    setTimeout(updateProgressBar, 1000);
  }

  document.addEventListener("DOMContentLoaded", updateProgressBar);
})();

function closeBanner() {
  const banner = document.getElementById('aiBanner');
  if (banner) {
    banner.style.display = 'none';
  }
}

