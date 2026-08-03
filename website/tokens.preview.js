// Review-harness script only (tokens.html). Not part of the component system.
const durationVar = (name) => `var(--yukti-duration-${name})`;
const easeVar = (name) => `var(--yukti-ease-${name})`;

document.querySelectorAll('.tp-motion-demo').forEach((btn) => {
  btn.addEventListener('click', () => {
    const duration = durationVar(btn.dataset.duration);
    const ease = easeVar(btn.dataset.ease);
    btn.style.transition = `transform ${duration} ${ease}, background ${duration} ${ease}`;
    btn.classList.add('tp-run');
    btn.style.transform = 'translateY(-6px)';
    setTimeout(() => {
      btn.classList.remove('tp-run');
      btn.style.transform = 'translateY(0)';
    }, 700);
  });
});
