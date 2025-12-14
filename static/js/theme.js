/**
 * AXON AI - THEME MANAGER
 * Handles Light/Dark mode persistence and toggling.
 * Runs immediately to prevent FOUC.
 */

(function () {
    // 1. Check for saved theme
    const savedTheme = localStorage.getItem('theme');

    // 2. Check system preference
    const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;

    // 3. Determine initial theme
    // Default to 'dark' unless explicitly 'light' or system prefers light and no partiality
    let initialTheme = 'dark';
    if (savedTheme) {
        initialTheme = savedTheme;
    } else if (systemPrefersLight) {
        initialTheme = 'light';
    }

    // 4. Apply theme immediately
    document.documentElement.setAttribute('data-theme', initialTheme);

    // 5. Expose toggle function globally
    window.toggleTheme = function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update all icons
        updateThemeIcons(newTheme);
    };

    // 6. Update Icons Helper
    function updateThemeIcons(theme) {
        // Find all theme toggle buttons/icons
        const icons = document.querySelectorAll('.theme-icon');

        icons.forEach(icon => {
            if (theme === 'light') {
                icon.textContent = '🌙'; // Moon for switching TO dark
            } else {
                icon.textContent = '☀️'; // Sun for switching TO light
            }
        });
    }

    // 7. Run icon update on DOMContentLoaded (once elements exist)
    document.addEventListener('DOMContentLoaded', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        updateThemeIcons(currentTheme);

        // Add click listeners to any new toggles
        const toggles = document.querySelectorAll('.theme-toggle');
        toggles.forEach(btn => {
            btn.addEventListener('click', window.toggleTheme);
        });
    });

})();
