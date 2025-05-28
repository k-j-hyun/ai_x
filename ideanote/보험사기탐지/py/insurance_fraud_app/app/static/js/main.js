document.addEventListener("DOMContentLoaded", function () {
    const track = document.querySelector('.carousel-track');
    const items = document.querySelectorAll('.carousel-item');
    const leftBtn = document.querySelectorAll('.carousel-btn')[0];
    const rightBtn = document.querySelectorAll('.carousel-btn')[1];
    
    let index = 0;

    function updateCarousel() {
        const width = items[0].offsetWidth + 10; // width + margin
        track.style.transform = `translateX(-${index * width}px)`;
    }

    leftBtn.addEventListener("click", () => {
        index = Math.max(index - 1, 0);
        updateCarousel();
    });

    rightBtn.addEventListener("click", () => {
        index = Math.min(index + 1, items.length - 1);
        updateCarousel();
    });
});