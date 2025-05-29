document.addEventListener("DOMContentLoaded", function () {
    // 캐러셀 기능
    const track = document.querySelector('.carousel-track');
    const items = document.querySelectorAll('.carousel-item');
    const leftBtn = document.querySelectorAll('.carousel-btn')[0];
    const rightBtn = document.querySelectorAll('.carousel-btn')[1];

    let index = 0;

    function updateCarousel() {
        const itemWidth = items[0].offsetWidth + 10; // margin 포함
        track.style.transform = `translateX(-${index * itemWidth}px)`;
    }

    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');

    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });

    leftBtn.addEventListener("click", () => {
        index = Math.max(index - 1, 0);
        updateCarousel();
    });

    rightBtn.addEventListener("click", () => {
        index = Math.min(index + 1, items.length - 1);
        updateCarousel();
    });

    // 배경 이미지 슬라이더
    const slides = document.querySelectorAll(".slide-image");
    let currentSlide = 0;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle("active", i === index);
        });
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    if (slides.length > 0) {
        showSlide(currentSlide);
        setInterval(nextSlide, 3000);
    }

    // 자동 슬라이드
    let slider = document.getElementById('imageSlider');

    function slideRight() {
        slider.scrollLeft += 320; // 이미지 한 장 너비 + gap
    }

    function slideLeft() {
        slider.scrollLeft -= 320;
    }

    setInterval(() => {
        slideRight();
    }, 4000); // 4초마다 자동 이동
});
