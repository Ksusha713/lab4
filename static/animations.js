document.addEventListener('DOMContentLoaded', () => {
    function wrapLetters(selector) {
        const el = document.querySelector(selector);
        if (el) { 
            el.innerHTML = el.textContent.replace(/\S/g, "<span class='letter'>$&</span>");
        }
    }

    wrapLetters('.animation');
    wrapLetters('.animation2');

    anime.timeline()
    .add({
        targets: '.animation .letter',
        opacity: [0, 1],
        translateY: [20, 0],
        easing: "easeOutExpo",
        duration: 300,
        delay: (el, i) => 40 * i
    })
    .add({
        targets: '.animation2 .letter',
        opacity: [0, 1],
        translateY: [20, 0],
        easing: "easeOutExpo",
        duration: 300,
        delay: (el, i) => 40 * i
    }, '-=100'); 
});