// VirtualHelpDesk - All Tables tab switching
document.addEventListener('DOMContentLoaded', function () {

    const tabs = document.querySelectorAll('.table-tab');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            const targetId = tab.dataset.target;

            // Deactivate all tabs/panels
            document.querySelectorAll('.table-tab').forEach(function (t) {
                t.classList.remove('active');
            });
            document.querySelectorAll('.table-panel').forEach(function (p) {
                p.classList.remove('active');
            });

            // Activate the selected one
            tab.classList.add('active');
            const panel = document.getElementById(targetId);
            if (panel) {
                panel.classList.add('active');
            }
        });
    });

});
