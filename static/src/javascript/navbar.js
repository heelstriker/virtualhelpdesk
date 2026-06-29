// VirtualHelpDesk - Navbar mobile toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('navbarToggle');
    const mobileMenu = document.getElementById('navbarMobileMenu');

    if (!toggleBtn || !mobileMenu) {
        return;
    }

    toggleBtn.addEventListener('click', function () {
        toggleBtn.classList.toggle('open');
        mobileMenu.classList.toggle('open');
    });

    // Close the mobile menu automatically when a link is tapped
    mobileMenu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            toggleBtn.classList.remove('open');
            mobileMenu.classList.remove('open');
        });
    });
});
