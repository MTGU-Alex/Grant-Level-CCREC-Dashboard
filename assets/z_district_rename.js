/**
 * assets/district_rename.js
 *
 * Handles all in-modal interaction for the district rename popup:
 *   - HTML5 drag-and-drop between the district pool and custom groups
 *   - "Add Group" button  →  creates a new drop-zone dynamically
 *   - "Remove Group" (✕) →  moves its districts back to the pool
 *
 * Uses event delegation on `document` so it survives Dash re-renders
 * of child components. The one-time flag prevents duplicate listeners.
 */
(function () {
    'use strict';

    var draggedItem = null;

    function setup() {
        if (window._districtRenameSetup) return;
        window._districtRenameSetup = true;

        /* ── Drag ─────────────────────────────────────────────────────── */
        document.addEventListener('dragstart', function (e) {
            var item = e.target.closest('.district-drag-item');
            if (!item) return;
            draggedItem = item;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', item.textContent.trim());
            setTimeout(function () { item.classList.add('dragging'); }, 0);
        });

        document.addEventListener('dragend', function () {
            if (draggedItem) {
                draggedItem.classList.remove('dragging');
                draggedItem = null;
            }
            document.querySelectorAll('.drag-over').forEach(function (el) {
                el.classList.remove('drag-over');
            });
        });

        document.addEventListener('dragover', function (e) {
            var zone = e.target.closest('.district-drop-zone');
            if (!zone) return;
            e.preventDefault();
            document.querySelectorAll('.district-drop-zone.drag-over').forEach(function (el) {
                if (el !== zone) el.classList.remove('drag-over');
            });
            zone.classList.add('drag-over');
        });

        document.addEventListener('dragleave', function (e) {
            var zone = e.target.closest('.district-drop-zone');
            if (!zone) return;
            if (!zone.contains(e.relatedTarget)) {
                zone.classList.remove('drag-over');
            }
        });

        document.addEventListener('drop', function (e) {
            var zone = e.target.closest('.district-drop-zone');
            if (zone) zone.classList.remove('drag-over');
            if (!zone || !draggedItem) return;
            // Guard: ensure the dragged item is still in the live document
            // (it may have been detached by a React re-render)
            if (!document.contains(draggedItem)) {
                draggedItem = null;
                return;
            }
            e.preventDefault();
            zone.appendChild(draggedItem);
            draggedItem.classList.remove('dragging');
            draggedItem = null;
        });

        /* ── Click delegation (Add Group + Remove Group) ──────────────── */
        document.addEventListener('click', function (e) {

            /* Add Group button */
            if (e.target.closest('#add-group-btn')) {
                e.preventDefault();
                var input = document.getElementById('new-group-name-input');
                if (!input) return;
                var name = input.value.trim();
                if (!name) return;

                var escapedName = name.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
                if (document.querySelector('.district-drop-zone[data-group="' + escapedName + '"]')) {
                    return;
                }

                var container = document.getElementById('groups-container');
                if (!container) return;

                var groupDiv = document.createElement('div');
                groupDiv.className = 'district-group';
                groupDiv.innerHTML =
                    '<div class="group-header">' +
                        '<span class="group-name-label">' + _esc(name) + '</span>' +
                        '<button class="remove-group-btn" title="Remove group">\u2715</button>' +
                    '</div>' +
                    '<div class="district-drop-zone" data-group="' + _esc(name) + '">' +
                        '<span class="drop-hint">Drop districts here</span>' +
                    '</div>';
                container.appendChild(groupDiv);
                input.value = '';
            }

            /* Remove Group (✕) button */
            var removeBtn = e.target.closest('.remove-group-btn');
            if (removeBtn) {
                var groupDiv = removeBtn.closest('.district-group');
                if (!groupDiv) return;
                var zone     = groupDiv.querySelector('.district-drop-zone');
                var pool     = document.getElementById('unassigned-drop-zone');
                if (zone && pool) {
                    Array.from(zone.querySelectorAll('.district-drag-item')).forEach(function (item) {
                        pool.appendChild(item);
                    });
                }
                groupDiv.remove();
            }
        });
    }

    function _esc(str) {
        return String(str)
            .replace(/&/g,  '&amp;')
            .replace(/</g,  '&lt;')
            .replace(/>/g,  '&gt;')
            .replace(/"/g,  '&quot;');
    }

    setup();
    setTimeout(setup, 300);
})();