/**
 * Network Diagram widget — VirtualHelpDesk / Banana Corporation
 * ---------------------------------------------------------------
 * Renders an interactive NOC-style topology (SVG) from a
 * {nodes:[], edges:[], drives:[]} payload — see /api/network/topology.
 *
 * Interactions:
 *   - Hover a node/edge   -> tooltip with live details
 *   - Double-click a node -> toggle that device Online / Offline
 *   - Click an edge       -> toggle that link Up / Severed
 *   - Downstream reachability is recomputed on every change, so a
 *     dead switch or a severed cable correctly grays out everything
 *     behind it (status "unreachable"), not just the thing you clicked.
 *   - The footer strip re-derives "share drive" availability from
 *     whichever file server / switch path backs each UNC path, so a
 *     dashboard can show "\\NYCSERVER01\Accounting Shared: DOWN"
 *     the moment that server's uplink is cut.
 *
 * Usage:
 *   <div id="nd-root" data-topology-url="/api/network/topology"></div>
 *   <script src="/static/js/network-diagram.js"></script>
 *   <script>NetworkDiagram.init(document.getElementById('nd-root'));</script>
 *
 * Or pass data directly: NetworkDiagram.init(el, { data: {...} })
 */
(function (global) {
  "use strict";

  const ROOT_IDS = ["MPLS-CLOUD-01"]; // graph is considered "backboned" from here
  const TYPE_ORDER = ["cloud", "router", "core_switch", "access_switch", "file_server", "pc_group", "printer_group"];

  const ICONS = {
    router: `<g class="nd-icon">
      <rect x="-16" y="-9" width="32" height="18" rx="3"/>
      <path d="M-16 0 H16"/>
      <path d="M-9 -9 V-15 L-4 -15" />
      <path d="M9 -9 V-15 L4 -15" />
      <path d="M-4 -15 l -2 -3 M-4 -15 l 2 -3" />
      <path d="M4 -15 l -2 -3 M4 -15 l 2 -3" />
    </g>`,
    core_switch: `<g class="nd-icon">
      <rect x="-17" y="-10" width="34" height="20" rx="2"/>
      <path d="M-11 -3 h22 M-11 3 h22"/>
      <path d="M-13 -10 v20 M13 -10 v20" stroke-opacity=".4"/>
    </g>`,
    access_switch: `<g class="nd-icon">
      <rect x="-15" y="-8" width="30" height="16" rx="2"/>
      <circle cx="-9" cy="0" r="1.4" fill="currentColor" stroke="none"/>
      <circle cx="-3" cy="0" r="1.4" fill="currentColor" stroke="none"/>
      <circle cx="3" cy="0" r="1.4" fill="currentColor" stroke="none"/>
      <circle cx="9" cy="0" r="1.4" fill="currentColor" stroke="none"/>
    </g>`,
    file_server: `<g class="nd-icon">
      <rect x="-11" y="-16" width="22" height="32" rx="2"/>
      <path d="M-11 -6 H11 M-11 4 H11"/>
      <circle cx="6" cy="-11" r="1.2" fill="currentColor" stroke="none"/>
      <circle cx="6" cy="-1" r="1.2" fill="currentColor" stroke="none"/>
      <circle cx="6" cy="9" r="1.2" fill="currentColor" stroke="none"/>
    </g>`,
    pc_group: `<g class="nd-icon">
      <rect x="-15" y="-12" width="20" height="14" rx="1.5"/>
      <rect x="-9" y="-6" width="20" height="14" rx="1.5"/>
      <path d="M-9 8 h20 M1 2 v6" transform="translate(0,0)"/>
    </g>`,
    printer_group: `<g class="nd-icon">
      <rect x="-13" y="-4" width="26" height="14" rx="2"/>
      <path d="M-9 -4 v-8 h18 v8"/>
      <rect x="-6" y="10" width="12" height="7" rx="1"/>
      <circle cx="9" cy="1" r="1.1" fill="currentColor" stroke="none"/>
    </g>`,
  };

  function cloudPath() {
    return `<g class="nd-icon">
      <path d="M-24 6 a10 10 0 0 1 2-19.7 a13 13 0 0 1 25 -3 a10 10 0 0 1 10 9.7 a9 9 0 0 1 -2 13 z" />
    </g>`;
  }

  const NODE_SIZE = {
    cloud: 46, router: 34, core_switch: 34, access_switch: 30,
    file_server: 32, pc_group: 30, printer_group: 30,
  };

  function statusClass(s) {
    if (!s) return "online";
    s = s.toLowerCase();
    if (s === "online" || s === "up") return "online";
    if (s === "degraded" || s === "warning") return "degraded";
    if (s === "unreachable") return "unreachable";
    return "offline";
  }

  function el(tag, attrs, html) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  class NetworkDiagram {
    constructor(root, opts) {
      this.root = root;
      this.opts = opts || {};
      this.overrides = { nodes: {}, edges: {} }; // manual online/offline & severed state
      this.scale = 1;
      this.pan = { x: 0, y: 0 };
      this.tooltipEl = null;
      this.build();
    }

    async build() {
      this.data = this.opts.data || await this.fetchData();
      this.index();
      this.hydrateOverridesFromServer();
      this.render();
      this.wireInteractions();
      this.recompute();
    }

    // The GET /api/network/topology response already merges any saved
    // network_override rows into each node's/edge's "status" field
    // (see network_topology_service.py). On first load we need to copy
    // that back into this.overrides so the client-side reachability
    // engine (which drives node/edge CSS classes and the footer share
    // panel) starts from the persisted DB state instead of assuming
    // everything is healthy. Without this, a refresh looks like the
    // toggle "reverted" even though it's still saved server-side.
    hydrateOverridesFromServer() {
      this.data.nodes.forEach((n) => {
        if ((n.status || "").toLowerCase() === "offline") {
          this.overrides.nodes[n.id] = "Offline";
        }
      });
      this.data.edges.forEach((e) => {
        if ((e.status || "").toLowerCase() === "severed") {
          this.overrides.edges[e.id] = "severed";
        }
      });
    }

    async fetchData() {
      const url = this.root.dataset.topologyUrl;
      if (!url) throw new Error("NetworkDiagram: no data and no data-topology-url set");
      const res = await fetch(url);
      return await res.json();
    }

    index() {
      this.nodesById = {};
      this.data.nodes.forEach((n) => (this.nodesById[n.id] = n));
      this.childrenOf = {};
      this.data.edges.forEach((e) => {
        (this.childrenOf[e.source] = this.childrenOf[e.source] || []).push(e);
      });
    }

    // ---------- rendering ----------
    render() {
      this.root.classList.add("nd-widget");
      const xs = this.data.nodes.map((n) => n.x);
      const ys = this.data.nodes.map((n) => n.y);
      const maxX = Math.max(...xs) + 90;
      const maxY = Math.max(...ys) + 90;
      const minX = Math.min(...xs) - 90;
      const minY = Math.min(...ys) - 60;
      this.viewBox = { minX, minY, w: maxX - minX, h: maxY - minY };

      this.root.innerHTML = `
        <div class="nd-header">
          <div class="nd-header-title">
            <h3>Network Topology</h3>
            <span class="nd-sub">NYC ⇄ LAX &middot; MPLS backbone</span>
          </div>
          <div class="nd-legend">
            <span><i class="nd-dot online"></i>Online</span>
            <span><i class="nd-dot warn"></i>Degraded</span>
            <span><i class="nd-dot crit"></i>Offline / Severed</span>
          </div>
          <div class="nd-toolbar">
            <button class="nd-btn" data-act="zoom-in" title="Zoom in">+</button>
            <button class="nd-btn" data-act="zoom-out" title="Zoom out">–</button>
            <button class="nd-btn" data-act="zoom-reset" title="Reset view">⤾</button>
            <button class="nd-btn" data-act="expand" title="Expand">⤢</button>
          </div>
        </div>
        <div class="nd-canvas-wrap">
          <svg class="nd-svg" viewBox="${minX} ${minY} ${this.viewBox.w} ${this.viewBox.h}"></svg>
          <div class="nd-tooltip"></div>
          <div class="nd-reset-toast">Simulation mode active — devices/links were toggled manually.<button data-act="sim-reset">Reset to live state</button></div>
        </div>
        <div class="nd-footer-section">
          <div class="nd-footer-title">Device Monitoring — Servers / Routers / Switches / Printers</div>
          <div class="nd-footer nd-device-board"></div>
        </div>
        <div class="nd-footer-section">
          <div class="nd-footer-title">Network Drive Access</div>
          <div class="nd-footer nd-drive-board"></div>
        </div>
      `;

      this.svg = this.root.querySelector("svg.nd-svg");
      this.tooltipEl = this.root.querySelector(".nd-tooltip");
      this.footerEl = this.root.querySelector(".nd-drive-board");
      this.deviceBoardEl = this.root.querySelector(".nd-device-board");
      this.canvasWrap = this.root.querySelector(".nd-canvas-wrap");
      this.toast = this.root.querySelector(".nd-reset-toast");

      this.edgeLayer = el("g", { class: "nd-edge-layer" });
      this.nodeLayer = el("g", { class: "nd-node-layer" });
      this.svg.appendChild(this.edgeLayer);
      this.svg.appendChild(this.nodeLayer);

      this.edgeEls = {};
      this.data.edges.forEach((e) => this.renderEdge(e));

      this.nodeEls = {};
      this.data.nodes.forEach((n) => this.renderNode(n));

      this.renderFooter();
      this.renderDeviceBoard();
    }

    edgePath(e) {
      const s = this.nodesById[e.source], t = this.nodesById[e.target];
      if (!s || !t) return "";
      if (e.type === "MPLS") {
        const midX = (s.x + t.x) / 2;
        const midY = Math.min(s.y, t.y) - 40;
        return `M${s.x},${s.y} Q${midX},${midY} ${t.x},${t.y}`;
      }
      // orthogonal elbow: down from source, across, down into target
      const midY = (s.y + t.y) / 2;
      return `M${s.x},${s.y} C${s.x},${midY} ${t.x},${midY} ${t.x},${t.y}`;
    }

    renderEdge(e) {
      const g = el("g", { class: "nd-edge-group", "data-id": e.id });
      const path = this.edgePath(e);
      const line = el("path", { class: "nd-edge", d: path });
      const hit = el("path", { class: "nd-edge-hit", d: path });
      g.appendChild(line);
      g.appendChild(hit);
      this.edgeLayer.appendChild(g);
      this.edgeEls[e.id] = { g, line, hit, data: e };
    }

    renderNode(n) {
      const size = NODE_SIZE[n.type] || 30;
      const g = el("g", { class: "nd-node", transform: `translate(${n.x},${n.y})`, "data-id": n.id });

      const shape =
        n.type === "cloud"
          ? el("ellipse", { class: "nd-node-shape", rx: size, ry: size * 0.62 })
          : el("rect", {
              class: "nd-node-shape",
              x: -size, y: -size * 0.72, width: size * 2, height: size * 1.44, rx: 10,
            });
      g.appendChild(shape);

      const ring =
        n.type === "cloud"
          ? el("ellipse", { class: "nd-status-ring", rx: size + 4, ry: size * 0.62 + 4 })
          : el("rect", {
              class: "nd-status-ring",
              x: -size - 4, y: -size * 0.72 - 4, width: size * 2 + 8, height: size * 1.44 + 8, rx: 12,
            });
      g.appendChild(ring);

      const iconHtml = n.type === "cloud" ? cloudPath() : ICONS[n.type] || "";
      const iconG = el("g", {});
      iconG.innerHTML = iconHtml;
      g.appendChild(iconG);

      const label = el("text", { class: "nd-node-label", y: size * 0.72 + 15 }, this.shortLabel(n));
      g.appendChild(label);
      if (n.type !== "cloud") {
        const sub = el("text", { class: "nd-node-sublabel", y: size * 0.72 + 27 }, this.subLabel(n));
        g.appendChild(sub);
      }

      if (n.count) {
        const bx = size - 6, by = -size * 0.72 + 4;
        const badgeBg = el("circle", { class: "nd-badge-bg", cx: bx, cy: by, r: 9 });
        const badgeTx = el("text", { class: "nd-badge", x: bx, y: by + 3.2 }, String(n.count));
        g.appendChild(badgeBg);
        g.appendChild(badgeTx);
      }

      this.nodeLayer.appendChild(g);
      this.nodeEls[n.id] = { g, data: n };
    }

    shortLabel(n) {
      if (n.type === "pc_group" || n.type === "printer_group") return n.label;
      return n.id;
    }
    subLabel(n) {
      if (n.type === "router") return "MPLS Router";
      if (n.type === "core_switch") return "Core L3";
      if (n.type === "access_switch") return "Access SW";
      if (n.type === "file_server") return n.role || "File Server";
      if (n.type === "pc_group") return `${n.department} · ${n.count} PCs`;
      if (n.type === "printer_group") return `${n.department} · ${n.count} printers`;
      return "";
    }

    renderFooter() {
      const cards = this.data.drives.map((d) => {
        const serverId = d.server.toUpperCase();
        const reachable = this.isReachable(serverId);
        return `
          <div class="nd-share-card ${reachable ? "" : "down"}" data-server="${serverId}">
            <div class="nd-share-name">${d.drive_letter} ${d.drive_name}</div>
            <div class="nd-share-path">${d.unc_path}</div>
            <div class="nd-share-status ${reachable ? "up" : "down"}">
              <i class="nd-dot ${reachable ? "online" : "crit"}"></i>
              ${reachable ? "ACCESSIBLE" : "ACCESS DENIED — server unreachable"}
            </div>
          </div>`;
      });
      this.footerEl.innerHTML = cards.join("");
    }

    // Cards for every switch/router/server/printer(/PC) node — the
    // "is this thing alive" board the Network Drive cards were modeled
    // after, just covering all monitored equipment instead of only the
    // file servers behind a share path.
    deviceBoardLabel(n) {
      const kind = {
        cloud: "MPLS Backbone",
        router: "Router",
        core_switch: "Core L3 Switch",
        access_switch: "Access Switch",
        file_server: "File Server",
        printer_group: "Printers",
        pc_group: "Workstations",
      }[n.type] || "Device";
      return kind;
    }

    deviceBoardDetail(n) {
      if (n.type === "file_server") return n.ip || n.role || "";
      if (n.type === "router" || n.type === "core_switch" || n.type === "access_switch" || n.type === "cloud") {
        return n.lan_ip && n.lan_ip !== "-" ? n.lan_ip : n.mgmt_ip || "";
      }
      if (n.type === "pc_group" || n.type === "printer_group") {
        return `${n.online_count ?? "?"} / ${n.count} online`;
      }
      return "";
    }

    renderDeviceBoard() {
      if (!this.deviceBoardEl) return;
      const order = { cloud: 0, router: 1, core_switch: 2, access_switch: 3, file_server: 4, printer_group: 5, pc_group: 6 };
      const sorted = [...this.data.nodes].sort((a, b) => {
        const byType = (order[a.type] ?? 9) - (order[b.type] ?? 9);
        if (byType !== 0) return byType;
        return (a.site || "").localeCompare(b.site || "") || a.id.localeCompare(b.id);
      });

      const cards = sorted.map((n) => {
        const st = this.isManuallyOffline(n.id) ? "offline" : !this.isReachable(n.id) ? "unreachable" : statusClass(n.status);
        const statusText = { online: "ONLINE", degraded: "DEGRADED", offline: "OFFLINE", unreachable: "UNREACHABLE" }[st];
        const dotClass = st === "online" ? "online" : st === "degraded" ? "warn" : "crit";
        const detail = this.deviceBoardDetail(n);
        return `
          <div class="nd-share-card ${st === "online" ? "" : "down"}" data-device="${n.id}">
            <div class="nd-share-name">${n.label || n.id}</div>
            <div class="nd-share-path">${this.deviceBoardLabel(n)}${detail ? " · " + detail : ""}</div>
            <div class="nd-share-status ${st === "online" ? "up" : "down"}">
              <i class="nd-dot ${dotClass}"></i>
              ${statusText}
            </div>
          </div>`;
      });
      this.deviceBoardEl.innerHTML = cards.join("");
    }

    // ---------- reachability / cascading state ----------
    isManuallyOffline(id) {
      return this.overrides.nodes[id] === "Offline";
    }
    isSevered(edgeId) {
      return this.overrides.edges[edgeId] === "severed";
    }

    recompute() {
      // BFS from root(s) across edges that aren't severed and whose endpoints
      // aren't manually offline. Anything not visited is "unreachable".
      const visited = new Set();
      const queue = [...ROOT_IDS];
      const adj = {};
      this.data.edges.forEach((e) => {
        if (this.isSevered(e.id)) return;
        (adj[e.source] = adj[e.source] || []).push(e.target);
        (adj[e.target] = adj[e.target] || []).push(e.source);
      });
      while (queue.length) {
        const cur = queue.shift();
        if (visited.has(cur)) continue;
        if (this.isManuallyOffline(cur)) continue;
        visited.add(cur);
        (adj[cur] || []).forEach((nb) => {
          if (!visited.has(nb) && !this.isManuallyOffline(nb)) queue.push(nb);
        });
      }
      this.reachable = visited;

      // apply node classes
      this.data.nodes.forEach((n) => {
        let status;
        if (this.isManuallyOffline(n.id)) status = "offline";
        else if (!visited.has(n.id)) status = "unreachable";
        else if (n.status === "Degraded" || (n.online_count !== undefined && n.online_count < n.count && n.online_count > 0)) status = "degraded";
        else status = "online";

        const { g } = this.nodeEls[n.id];
        g.classList.remove("status-online", "status-degraded", "status-offline", "status-unreachable");
        g.classList.add(`status-${status}`);
      });

      // apply edge classes
      this.data.edges.forEach((e) => {
        const { line } = this.edgeEls[e.id];
        line.classList.remove("status-up", "status-mpls", "status-warning", "status-critical", "status-severed", "status-unreachable");
        if (this.isSevered(e.id)) {
          line.classList.add("status-severed");
        } else if (this.isManuallyOffline(e.source) || this.isManuallyOffline(e.target) || !visited.has(e.source) || !visited.has(e.target)) {
          line.classList.add("status-unreachable");
        } else if (e.type === "MPLS") {
          line.classList.add("status-mpls");
        } else if (e.alarm === "Critical") {
          line.classList.add("status-critical");
        } else if (e.alarm === "Warning") {
          line.classList.add("status-warning");
        } else {
          line.classList.add("status-up");
        }
      });

      this.renderFooter();
      this.renderDeviceBoard();
      this.updateToast();
    }

    isReachable(nodeId) {
      return this.reachable && this.reachable.has(nodeId) && !this.isManuallyOffline(nodeId);
    }

    updateToast() {
      const dirty = Object.keys(this.overrides.nodes).length || Object.keys(this.overrides.edges).length;
      this.toast.classList.toggle("visible", !!dirty);
    }

    // ---------- interactions ----------
    wireInteractions() {
      this.root.addEventListener("click", (ev) => {
        const btn = ev.target.closest("[data-act]");
        if (!btn) return;
        const act = btn.dataset.act;
        if (act === "zoom-in") this.zoom(1.2);
        if (act === "zoom-out") this.zoom(1 / 1.2);
        if (act === "zoom-reset") this.resetView();
        if (act === "expand") this.toggleExpand();
        if (act === "sim-reset") this.resetSimulation();
      });

      this.nodeLayer.addEventListener("dblclick", (ev) => {
        const g = ev.target.closest(".nd-node");
        if (!g) return;
        const id = g.dataset.id;
        const current = this.overrides.nodes[id] === "Offline" ? "Online" : "Offline";
        if (current === "Online") delete this.overrides.nodes[id];
        else this.overrides.nodes[id] = "Offline";
        this.recompute();
        this.opts.onNodeToggle && this.opts.onNodeToggle(id, current);
        ev.preventDefault();
      });

      this.edgeLayer.addEventListener("click", (ev) => {
        const g = ev.target.closest(".nd-edge-group");
        if (!g) return;
        const id = g.dataset.id;
        const nowSevered = this.overrides.edges[id] !== "severed";
        if (nowSevered) this.overrides.edges[id] = "severed";
        else delete this.overrides.edges[id];
        this.recompute();
        this.opts.onLinkToggle && this.opts.onLinkToggle(id, nowSevered ? "severed" : "up");
      });

      // hover tooltips
      this.svg.addEventListener("mousemove", (ev) => {
        const nodeG = ev.target.closest(".nd-node");
        const edgeG = ev.target.closest(".nd-edge-group");
        if (nodeG) this.showTooltip(this.nodesById[nodeG.dataset.id], ev, "node");
        else if (edgeG) this.showTooltip(this.edgeEls[edgeG.dataset.id].data, ev, "edge");
        else this.hideTooltip();
      });
      this.svg.addEventListener("mouseleave", () => this.hideTooltip());

      // pan
      let dragging = false, start = { x: 0, y: 0 }, panStart = { x: 0, y: 0 };
      this.canvasWrap.addEventListener("mousedown", (ev) => {
        if (ev.target.closest(".nd-node") || ev.target.closest(".nd-edge-group")) return;
        dragging = true;
        this.canvasWrap.classList.add("dragging");
        start = { x: ev.clientX, y: ev.clientY };
        panStart = { ...this.pan };
      });
      window.addEventListener("mousemove", (ev) => {
        if (!dragging) return;
        const dx = (ev.clientX - start.x) / this.scale;
        const dy = (ev.clientY - start.y) / this.scale;
        this.pan = { x: panStart.x - dx, y: panStart.y - dy };
        this.applyTransform();
      });
      window.addEventListener("mouseup", () => {
        dragging = false;
        this.canvasWrap.classList.remove("dragging");
      });

      // wheel zoom
      this.canvasWrap.addEventListener(
        "wheel",
        (ev) => {
          ev.preventDefault();
          this.zoom(ev.deltaY < 0 ? 1.08 : 1 / 1.08);
        },
        { passive: false }
      );
    }

    zoom(factor) {
      this.scale = Math.min(3, Math.max(0.5, this.scale * factor));
      this.applyTransform();
    }
    resetView() {
      this.scale = 1;
      this.pan = { x: 0, y: 0 };
      this.applyTransform();
    }
    applyTransform() {
      const vb = this.viewBox;
      const w = vb.w / this.scale;
      const h = vb.h / this.scale;
      const cx = vb.minX + vb.w / 2 + this.pan.x;
      const cy = vb.minY + vb.h / 2 + this.pan.y;
      this.svg.setAttribute("viewBox", `${cx - w / 2} ${cy - h / 2} ${w} ${h}`);
    }
    toggleExpand() {
      this.root.classList.toggle("nd-expanded");
    }
    resetSimulation() {
      this.overrides = { nodes: {}, edges: {} };
      this.recompute();
    }

    showTooltip(d, ev, kind) {
      if (!d) return;
      const rect = this.canvasWrap.getBoundingClientRect();
      const x = ev.clientX - rect.left + 14;
      const y = ev.clientY - rect.top + 14;
      let html = "";
      if (kind === "node") {
        const st = this.isManuallyOffline(d.id) ? "Offline" : !this.isReachable(d.id) ? "Unreachable" : d.status;
        html = `<div class="nd-tt-title"><i class="nd-dot ${statusDot(st)}"></i>${d.id}</div>`;
        if (d.model) html += row("Model", `${d.vendor || ""} ${d.model}`);
        if (d.lan_ip && d.lan_ip !== "-") html += row("LAN IP", d.lan_ip);
        if (d.mgmt_ip && d.mgmt_ip !== "-") html += row("Mgmt IP", d.mgmt_ip);
        if (d.ip) html += row("IP", d.ip);
        if (d.firmware) html += row("Firmware", d.firmware);
        if (d.count) html += row("Devices", `${d.online_count ?? "?"}/${d.count} online`);
        if (d.role) html += row("Role", d.role);
        html += row("Status", st);
        html += `<div class="nd-tt-hint">Double-click to toggle online/offline</div>`;
      } else {
        const severed = this.isSevered(d.id);
        html = `<div class="nd-tt-title"><i class="nd-dot ${severed ? "crit" : "online"}"></i>${d.source} → ${d.target}</div>`;
        html += row("Link type", d.type);
        if (d.bandwidth) html += row("Bandwidth", d.bandwidth);
        if (d.latency_ms) html += row("Latency", d.latency_ms);
        if (d.utilization_pct) html += row("Utilization", d.utilization_pct);
        if (d.packet_loss_pct) html += row("Packet loss", d.packet_loss_pct);
        html += row("Status", severed ? "Severed (simulated)" : d.status);
        html += `<div class="nd-tt-hint">Click cable to sever / restore</div>`;
      }
      this.tooltipEl.innerHTML = html;
      this.tooltipEl.style.left = x + "px";
      this.tooltipEl.style.top = y + "px";
      this.tooltipEl.classList.add("visible");
    }
    hideTooltip() {
      this.tooltipEl.classList.remove("visible");
    }
  }

  function statusDot(s) {
    s = (s || "").toLowerCase();
    if (s === "online" || s === "up") return "online";
    if (s === "degraded" || s === "warning") return "warn";
    return "crit";
  }
  function row(label, value) {
    return `<div class="nd-tt-row"><span>${label}</span><b>${value}</b></div>`;
  }

  global.NetworkDiagram = {
    init(el, opts) {
      return new NetworkDiagram(el, opts || {});
    },
  };
})(window);
