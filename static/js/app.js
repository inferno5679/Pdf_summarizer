function smoothScroll(targetSelector, duration) {
  var target = document.querySelector(targetSelector);
  var targetPosition = target.getBoundingClientRect().top;
  var startPosition = window.scrollY;
  var distance = targetPosition - startPosition;
  var startTime = null;

  function animation(currentTime) {
      if (startTime === null) {
          startTime = currentTime;
      }
      var timeElapsed = currentTime - startTime;
      var run = ease(timeElapsed, startPosition, distance, duration);
      window.scrollTo(0, run);
      if (timeElapsed < duration) {
          requestAnimationFrame(animation);
      }
  }

  function ease(t, b, c, d) {
      t /= d / 2;
      if (t < 1) {
          return (c / 2) * t * t + b;
      }
      t--;
      return (-c / 2) * (t * (t - 2) - 1) + b;
  }

  requestAnimationFrame(animation);
}

document.addEventListener("DOMContentLoaded", function() {
  var section1 = document.querySelector(".btn.summarize_button");
  section1.addEventListener("click", function (event) {
      // event.preventDefault();
      smoothScroll(".summary", 1500);
  });
});
