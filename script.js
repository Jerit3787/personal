// Dark mode toggle functionality
const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const themeText = document.querySelector('.theme-mode');

// Check for saved theme preference or prefer-color-scheme
function getCurrentTheme() {
    return localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

// Set initial theme
function setTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        toggleSwitch.checked = true;
        themeText.textContent = 'Dark';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        toggleSwitch.checked = false;
        themeText.textContent = 'Light';
    }
}

// Initialize theme
setTheme(getCurrentTheme());

// Listen for theme change
toggleSwitch.addEventListener('change', function (e) {
    if (e.target.checked) {
        setTheme('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        setTheme('light');
        localStorage.setItem('theme', 'light');
    }
});

// Add subtle entrance animation to social link cards
document.addEventListener('DOMContentLoaded', function () {
    const panels = document.querySelectorAll('.profilePanel, .linkButton');

    panels.forEach((panel, index) => {
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(20px)';
        panel.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        setTimeout(() => {
            panel.style.opacity = '1';
            panel.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});