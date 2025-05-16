  const totalSeconds = window.remainingTime || 300;
  let timeLeft = totalSeconds;

  const circle = document.getElementById('progress-circle');
  const label = document.getElementById('countdown-label');

  function updateCountdown() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    label.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    const progress = (timeLeft / totalSeconds) * 100;
    circle.setAttribute('stroke-dasharray', `${progress}, 100`);

    if (timeLeft > 0) {
      timeLeft--;
      setTimeout(updateCountdown, 1000);
    } else {
      label.textContent = 'Expired';
      circle.setAttribute('stroke', '#c00');
    }
  }

  updateCountdown();
