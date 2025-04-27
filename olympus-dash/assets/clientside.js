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

// Wait for the DOM to be fully loaded before running the script
window.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed, attaching sidebar handlers.');
    
    // CREATE A MAP OF ICON POSITIONS TO URLS FOR DIRECT NAVIGATION
    function setupSidebarIconNavigation() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;
        
        // Get all navigation links
        const navLinks = document.querySelectorAll('#sidebar-navigation-links a');
        const iconPositions = [];
        
        // Store all the icon positions and their URLs
        navLinks.forEach((link, index) => {
            const icon = link.querySelector('i');
            if (icon) {
                const href = link.getAttribute('href');
                iconPositions.push({
                    index: index,
                    href: href,
                    link: link
                });
            }
        });
        
        // Function to handle clicks on the collapsed sidebar
        function handleSidebarClick(e) {
            // Only process if sidebar is not active (collapsed)
            if (sidebar.classList.contains('active')) return;
            
            // Get mouse position relative to sidebar
            const rect = sidebar.getBoundingClientRect();
            const y = e.clientY - rect.top;
            
            // Roughly calculate which icon was clicked based on vertical position
            // This assumes icons are evenly spaced or at least in predictable positions
            // The index depends on actual DOM structure and spacing
            
            const headerHeight = 100; // Approximate pixel height of sidebar header including padding and margin
            const iconHeight = 50;   // Approximate pixel height for each icon including padding
            
            // Calculate which icon might have been clicked (0-indexed)
            const clickedIndex = Math.floor((y - headerHeight) / iconHeight);
            
            // Find the matching link URL
            const matchingPosition = iconPositions.find(pos => pos.index === clickedIndex);
            
            if (matchingPosition && matchingPosition.href) {
                // Prevent sidebar expansion
                e.preventDefault();
                e.stopPropagation();
                
                // Navigate directly
                console.log(`Direct navigation from sidebar overlay click to: ${matchingPosition.href}`);
                window.location.href = matchingPosition.href;
            }
        }
        
        // Attach click handler to the sidebar element itself
        sidebar.addEventListener('click', handleSidebarClick);
    }
    
    // Set up the sidebar icon navigation
    setTimeout(setupSidebarIconNavigation, 500);
    
    // DIRECT FIX FOR SIDEBAR ICON NAVIGATION ISSUE - KEEP THIS TOO
    function fixSidebarNavigationIcons() {
        // The most direct approach - completely replace icons with direct navigation
        document.addEventListener('click', function(e) {
            // Look for any icon or link in the sidebar
            let targetElement = e.target;
            let isIcon = false;
            let navLink = null;
            
            // Check if clicked element is an icon or if its parent is a nav-link
            if (targetElement.tagName === 'I' && targetElement.closest('.sidebar-nav-items')) {
                isIcon = true;
                navLink = targetElement.closest('a');
            } else if (targetElement.closest('.sidebar-nav-items a')) {
                navLink = targetElement.closest('a');
            }
            
            // If we found a navigation link
            if (navLink) {
                const sidebar = document.getElementById('sidebar');
                // Only override behavior if sidebar is collapsed
                if (sidebar && !sidebar.classList.contains('active')) {
                    // Prevent the default behavior which would expand the sidebar
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Get the link destination
                    const href = navLink.getAttribute('href');
                    
                    // Navigate directly
                    if (href) {
                        console.log(`Direct navigation to: ${href}`);
                        window.location.href = href;
                    }
                    
                    // Return false to stop other handlers
                    return false;
                }
            }
        }, true); // Using capture phase to intercept before other handlers
    }
    
    // Run the fix immediately
    fixSidebarNavigationIcons();
    
    // Track sidebar state directly
    let sidebarWasCollapsed = false;
    
    // Override sidebar toggle behavior
    function setupSidebarControls() {
        const sidebarToggleBtn = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        const navLinks = document.querySelectorAll('#sidebar-navigation-links a');
        
        if (sidebar && navLinks.length > 0) {
            // Store original href attributes to restore them later
            const originalHrefs = Array.from(navLinks).map(link => link.getAttribute('href'));
            
            // Monitor sidebar class changes to detect when it collapses/expands
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        const isCollapsed = !sidebar.classList.contains('active');
                        
                        // Update links based on sidebar state
                        if (isCollapsed) {
                            // When sidebar is collapsed, make links navigate directly without toggling
                            navLinks.forEach((link, index) => {
                                const href = originalHrefs[index];
                                
                                // Replace the link with a direct JavaScript navigation
                                link.setAttribute('data-href', href);
                                link.removeAttribute('href');
                                
                                // Use onclick instead of href
                                link.onclick = function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    window.location.href = this.getAttribute('data-href');
                                    return false;
                                };
                            });
                        } else {
                            // When sidebar is expanded, restore normal link behavior
                            navLinks.forEach((link, index) => {
                                const href = link.getAttribute('data-href') || originalHrefs[index];
                                link.setAttribute('href', href);
                                link.removeAttribute('data-href');
                                link.onclick = null;
                            });
                        }
                    }
                });
            });
            
            // Start observing the sidebar for class changes
            observer.observe(sidebar, { attributes: true });
            
            // Initial setup based on current sidebar state
            if (!sidebar.classList.contains('active')) {
                // Sidebar is already collapsed, set direct navigation
                navLinks.forEach((link, index) => {
                    const href = originalHrefs[index];
                    link.setAttribute('data-href', href);
                    link.removeAttribute('href');
                    link.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        window.location.href = this.getAttribute('data-href');
                        return false;
                    };
                });
            }
        }
    }
    
    // Initialize sidebar controls after a short delay to ensure the DOM is ready
    setTimeout(setupSidebarControls, 500);

    // Original sidebar link handlers (can keep these as fallback)
    function attachSidebarLinkListeners() {
        // In Dash with Bootstrap components, the actual links are within the nav-item elements
        const sidebarNavContainer = document.getElementById('sidebar-navigation-links');
        const closeButton = document.getElementById('close-sidebar-btn');

        if (sidebarNavContainer && closeButton) {
            // Target all anchor tags within the navigation container
            // This more general selector ensures we catch the links regardless of exact DOM structure
            const navLinks = sidebarNavContainer.getElementsByTagName('a');
            
            console.log(`Found ${navLinks.length} nav links in sidebar.`);

            Array.from(navLinks).forEach(link => {
                // Remove any existing listener to prevent duplicates
                link.removeEventListener('click', handleNavLinkClick);
                // Add the new listener
                link.addEventListener('click', handleNavLinkClick);
            });
        } else {
            console.error('Required elements not found:', {
                'sidebar-navigation-links': !!sidebarNavContainer,
                'close-sidebar-btn': !!closeButton
            });
            // Retry if elements aren't ready yet
            setTimeout(attachSidebarLinkListeners, 500);
        }
    }

    function handleNavLinkClick(e) {
        console.log('Navigation link clicked');
        const sidebar = document.getElementById('sidebar');
        const closeButton = document.getElementById('close-sidebar-btn');
        
        if (sidebar && closeButton) {
            console.log('Sidebar active state:', sidebar.classList.contains('active'));
            
            // If sidebar is open, click the close button
            if (sidebar.classList.contains('active')) {
                console.log('Closing sidebar');
                closeButton.click();
            }
        }
    }

    // Initial attempt to attach listeners
    attachSidebarLinkListeners();

    // Also attach listeners when the page loads/changes
    document.addEventListener('load', attachSidebarLinkListeners);
    
    // FALLBACK APPROACH: Add a click event listener to the entire sidebar
    // This catches any click within the sidebar that might be a navigation event
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.addEventListener('click', function(e) {
            // Check if the clicked element or any of its parents is an anchor tag
            let target = e.target;
            while (target && target !== this) {
                if (target.tagName === 'A') {
                    const closeButton = document.getElementById('close-sidebar-btn');
                    if (closeButton && sidebar.classList.contains('active')) {
                        console.log('Link clicked within sidebar, closing sidebar');
                        // Small timeout to ensure the navigation starts before closing
                        setTimeout(() => closeButton.click(), 10);
                    }
                    break;
                }
                target = target.parentElement;
            }
        });
    }
    
    // Listen for changes to the page content (which happens during navigation)
    const pageContent = document.getElementById('page-content');
    if (pageContent) {
        const contentObserver = new MutationObserver((mutationsList, observer) => {
            const sidebar = document.getElementById('sidebar');
            const closeButton = document.getElementById('close-sidebar-btn');
            
            if (sidebar && closeButton && sidebar.classList.contains('active')) {
                console.log('Page content changed, closing sidebar if open');
                closeButton.click();
            }
        });
        
        contentObserver.observe(pageContent, { 
            childList: true, 
            subtree: false 
        });
        console.log("Content change observer attached");
    }
    
    // Attach a MutationObserver to handle dynamic updates to the sidebar
    const observerTarget = document.getElementById('sidebar');
    if (observerTarget) {
        const observer = new MutationObserver((mutationsList, observer) => {
            for(let mutation of mutationsList) {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    console.log('Sidebar content changed, re-attaching listeners');
                    // Use setTimeout to ensure DOM is fully updated
                    setTimeout(attachSidebarLinkListeners, 100);
                    // Also refresh sidebar controls
                    setTimeout(setupSidebarControls, 100);
                    break;
                }
            }
        });

        observer.observe(observerTarget, { 
            childList: true, 
            subtree: true,
            attributes: true 
        });
        console.log("MutationObserver attached to sidebar");
    }
}); 