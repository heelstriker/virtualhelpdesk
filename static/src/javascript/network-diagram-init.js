/**
 * network-diagram-init.js
 * ---------------------------------------------------------------
 * Boots the Network Topology widget on the Dashboard page.
 *
 * Deliberately kept in its own external file (not an inline
 * <script> inside the Jinja partial): inline <script> blocks live
 * inside HTML templates, and if anything in the deployment pipeline
 * ever collapses that HTML onto fewer lines (a minifier, whitespace
 * stripping, etc.), any `//` line comment silently eats the rest of
 * the line — including real code after it — with no visible error.
 * External .js files aren't touched by HTML minifiers, so this file
 * is safe to comment normally.
 */
document.addEventListener("DOMContentLoaded", function () {
  var root = document.getElementById("nd-root");
  if (!root || typeof NetworkDiagram === "undefined") return;

  NetworkDiagram.init(root, {
    /* Persist simulated toggles back to the server. The server-side
       cascade (services/network_topology_service.py) then writes
       through to the real `devices` table, and refreshDashboardLive()
       pulls the updated Alerts / Device Status / Risk table in place —
       no page reload needed. */
    onNodeToggle: function (deviceId, newStatus) {
      fetch("/api/network/device/" + deviceId + "/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      })
        .then(function () {
          if (window.refreshDashboardLive) window.refreshDashboardLive();
        })
        .catch(function () {});
    },
    onLinkToggle: function (linkId, newStatus) {
      fetch("/api/network/link/" + linkId + "/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      })
        .then(function () {
          if (window.refreshDashboardLive) window.refreshDashboardLive();
        })
        .catch(function () {});
    },
  });
});
