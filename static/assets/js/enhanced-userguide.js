window.addEventListener('load', function (event) {
        applyActiveClass();
});

window.addEventListener('hashchange', function (event) {
    applyActiveClass();
});
// Function to apply the active class based on the current URL hash
function applyActiveClass() {
    let window_hash = window.location.hash;
    let anchors = document.querySelectorAll('.moj-side-navigation__item a');
    anchors.forEach(anchor => {
        // Check if the anchor's href matches the current hash
        let href = anchor.getAttribute('href');
        let hash = href.split('#')[1]; // Extract the hash part from the href
        if (window_hash === '#' + hash) {
            // If it matches, add the active class to the parent li
            anchor.parentElement.classList.add('moj-side-navigation__item--active');
            anchor.parentElement.ariaCurrent = 'location';
        } else {
            anchor.parentElement.classList.remove('moj-side-navigation__item--active');
            anchor.parentElement.ariaCurrent = 'false';
        }
    });
}
