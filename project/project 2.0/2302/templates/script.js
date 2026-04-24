// ===== Анимация появления элементов при загрузке страницы =====
document.addEventListener('DOMContentLoaded', () => {
    const fadeElements = document.querySelectorAll('.menu-container, .container, form, .flash-messages');
    fadeElements.forEach((el, index) => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.6s ease-out';
            el.style.opacity = 1;
            el.style.transform = 'translateY(0)';
        }, index * 150);
    });
});

// ===== Анимация нажатия кнопок =====
const buttons = document.querySelectorAll('button');
buttons.forEach(button => {
    button.addEventListener('mousedown', () => {
        button.style.transform = 'scale(0.95)';
    });
    button.addEventListener('mouseup', () => {
        button.style.transform = 'scale(1)';
    });
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'scale(1)';
    });
});

// ===== Плавное появление flash-сообщений =====
const flashMessages = document.querySelectorAll('.flash-messages');
flashMessages.forEach(msg => {
    msg.style.opacity = 0;
    msg.style.transition = 'opacity 1s ease';
    setTimeout(() => {
        msg.style.opacity = 1;
    }, 100);
    setTimeout(() => {
        msg.style.opacity = 0;
        setTimeout(() => msg.remove(), 1000);
    }, 5000);
});

// ===== Подсветка кнопок меню при наведении =====
const menuButtons = document.querySelectorAll('.menu-container button');
menuButtons.forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.boxShadow = '0 8px 15px rgba(0,0,0,0.2)';
    });
    button.addEventListener('mouseleave', () => {
        button.style.boxShadow = 'none';
    });
});