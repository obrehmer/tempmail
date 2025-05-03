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

