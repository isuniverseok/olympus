if(!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    observer: null,
    lastValue: null,
    
    setupAnimations: function() {
        // Clean up existing observer
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        // Initialize elements
        const elements = document.querySelectorAll('.performance-card, .chart-card, .analysis-card, .js-plotly-plot');
        elements.forEach(el => {
            el.classList.remove('animate-slide', 'animate-ready');
            void el.offsetWidth; // Force reflow
            el.classList.add('animate-ready');
        });

        // Create new observer with multiple thresholds for smoother detection
        this.observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && entry.target.classList.contains('animate-ready')) {
                        // Only trigger animation when element is sufficiently visible
                        if (entry.intersectionRatio >= 0.15) {
                            entry.target.classList.remove('animate-ready');
                            void entry.target.offsetWidth; // Force reflow
                            entry.target.classList.add('animate-slide');
                            this.observer.unobserve(entry.target);
                        }
                    }
                });
            },
            {
                // Multiple thresholds for smoother detection
                threshold: [0, 0.15, 0.3],
                // Start observing earlier and continue slightly after element passes
                rootMargin: '100px 0px -10% 0px'
            }
        );

        // Start observing elements
        elements.forEach(el => this.observer.observe(el));
    }
};

// Handle both initial load and content changes
function initializeAndWatchAnimations() {
    // Set up mutation observer to watch for content changes
    const contentObserver = new MutationObserver((mutations) => {
        let shouldAnimate = false;
        
        for (const mutation of mutations) {
            // Check if this is a relevant change
            if (mutation.type === 'childList' && 
                (mutation.target.id === 'country-profile-visuals' || 
                 mutation.target.closest('#country-profile-visuals'))) {
                shouldAnimate = true;
                break;
            }
        }
        
        if (shouldAnimate) {
            // Wait for content to be fully rendered
            setTimeout(() => {
                window.dash_clientside.clientside.setupAnimations();
            }, 100);
        }
    });

    // Watch for dropdown changes
    function setupDropdownWatcher() {
        const dropdown = document.querySelector('input[aria-autocomplete="list"]');
        if (dropdown) {
            // Watch for value changes
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                        const newValue = dropdown.value;
                        if (newValue !== window.dash_clientside.clientside.lastValue) {
                            window.dash_clientside.clientside.lastValue = newValue;
                            setTimeout(() => {
                                window.dash_clientside.clientside.setupAnimations();
                            }, 300); // Increased delay to ensure content is updated
                        }
                    }
                });
            });
            
            observer.observe(dropdown, {
                attributes: true,
                attributeFilter: ['value']
            });
        } else {
            // If dropdown not found, retry after a short delay
            setTimeout(setupDropdownWatcher, 100);
        }
    }

    // Start observing the document for content changes
    const visuals = document.getElementById('country-profile-visuals');
    if (visuals) {
        // Initial setup
        window.dash_clientside.clientside.setupAnimations();
        
        // Watch for changes
        contentObserver.observe(visuals, {
            childList: true,
            subtree: true
        });
        
        // Setup dropdown watcher
        setupDropdownWatcher();
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAndWatchAnimations);
} else {
    initializeAndWatchAnimations();
} 