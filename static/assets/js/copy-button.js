document.addEventListener('DOMContentLoaded', () => {
    const copyButton = document.getElementById('copyButton');
    if (copyButton) {
        copyButton.addEventListener('click', () => {
            const linkToCopy = window.location.href; // Or any specific link
            navigator.clipboard.writeText(linkToCopy)
                .then(() => {
                    // Change button text
                    copyButton.innerText = 'Link Copied';
                    copyButton.disabled = true; // Optional: Disable button to prevent repeated clicks
                    setTimeout(() => {
                        copyButton.innerText = 'Copy Link'; // Reset text after 3 seconds
                        copyButton.disabled = false;
                    }, 3000);
                })
                .catch(err => console.error('Failed to copy: ', err));
        });
    }
});
