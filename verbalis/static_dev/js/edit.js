(function () {
    const planArea      = document.getElementById('plan-area');
    const availableArea = document.getElementById('available-area');
    const saveBtn       = document.getElementById('save-btn');
    const saveStatus    = document.getElementById('save-status');
    const PUZZLE_IMG    = window.PUZZLE_IMG || '';

    /* ── SortableJS ─────────────────────────────────────── */
    Sortable.create(planArea, {
        animation: 180,
        ghostClass:  'sortable-ghost',
        chosenClass: 'sortable-chosen',
        onEnd: updateBadges,
    });

    /* ── Remove ─────────────────────────────────────────── */
    planArea.addEventListener('click', function (e) {
        const btn = e.target.closest('.module-remove-btn');
        if (!btn) return;
        const card = btn.closest('.module-card-edit');
        if (!card) return;

        if (availableArea) {
            availableArea.appendChild(makeAvailableCard(card.dataset.id, card.dataset.displayed));
        }
        card.remove();
        updateBadges();
        updateEmptyHint();
    });

    /* ── Add ─────────────────────────────────────────────── */
    if (availableArea) {
        availableArea.addEventListener('click', function (e) {
            const card = e.target.closest('.module-card-available');
            if (!card) return;

            planArea.appendChild(makePlanCard(card.dataset.id, card.dataset.displayed));
            card.remove();
            updateBadges();
            updateEmptyHint();
        });
    }

    /* ── Save ────────────────────────────────────────────── */
    saveBtn.addEventListener('click', function () {
        const ids = Array.from(
            planArea.querySelectorAll('.module-card-edit')
        ).map(c => parseInt(c.dataset.id));

        saveBtn.disabled = true;
        saveStatus.textContent = '';

        fetch(window.EDIT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN,
            },
            body: JSON.stringify({ modules: ids }),
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'ok') {
                saveStatus.textContent = '✓ Сохранено';
                saveStatus.style.color = 'green';
            } else {
                saveStatus.textContent = 'Ошибка сохранения';
                saveStatus.style.color = 'red';
            }
        })
        .catch(() => {
            saveStatus.textContent = 'Ошибка соединения';
            saveStatus.style.color = 'red';
        })
        .finally(() => { saveBtn.disabled = false; });
    });

    /* ── Helpers ─────────────────────────────────────────── */
    function makePlanCard(id, displayed) {
        const div = document.createElement('div');
        div.className = 'module-card-edit';
        div.dataset.id = id;
        div.dataset.displayed = displayed;
        div.innerHTML =
            `<img src="${PUZZLE_IMG}" alt="">` +
            `<div class="module-overlay"><span>${displayed}</span></div>` +
            `<span class="drag-order-badge"></span>` +
            `<button class="module-remove-btn" title="Убрать">×</button>`;
        return div;
    }

    function makeAvailableCard(id, displayed) {
        const div = document.createElement('div');
        div.className = 'module-card-available';
        div.dataset.id = id;
        div.dataset.displayed = displayed;
        div.innerHTML =
            `<img src="${PUZZLE_IMG}" alt="">` +
            `<div class="module-overlay"><span>${displayed}</span></div>` +
            `<div class="module-add-badge">+</div>`;
        return div;
    }

    function updateBadges() {
        planArea.querySelectorAll('.module-card-edit').forEach((card, i) => {
            const b = card.querySelector('.drag-order-badge');
            if (b) b.textContent = i + 1;
        });
    }

    function updateEmptyHint() {
        const cards = planArea.querySelectorAll('.module-card-edit');
        let hint = planArea.querySelector('.empty-plan-hint');
        if (cards.length === 0) {
            if (!hint) {
                hint = document.createElement('span');
                hint.className = 'empty-plan-hint';
                hint.textContent = 'Добавьте модули из списка ниже';
                planArea.appendChild(hint);
            }
        } else if (hint) {
            hint.remove();
        }
    }

    updateBadges();
})();