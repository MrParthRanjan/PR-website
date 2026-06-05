// Dark Mode Toggle

const darkModeToggle = document.getElementById('darkModeToggle');
const html = document.documentElement;

// Check for saved dark mode preference
const savedDarkMode = localStorage.getItem('darkMode');
if (savedDarkMode === 'enabled') {
    document.body.classList.add('dark-mode');
    updateToggleButton(true);
}

// Toggle dark mode
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
        updateToggleButton(isDarkMode);
    });
}

function updateToggleButton(isDarkMode) {
    if (darkModeToggle) {
        darkModeToggle.textContent = isDarkMode ? '☀️' : '🌙';
    }
}

console.log('✅ Dark mode initialized!');
