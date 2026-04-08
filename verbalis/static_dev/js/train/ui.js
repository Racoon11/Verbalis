export function createButton() {
    const btnDiv = document.createElement('div');
    btnDiv.className = 'col-6 d-flex justify-content-center';
    const btn = document.createElement('button');
    btn.className = 'plus-button detail clickable-word train-button';
    btnDiv.appendChild(btn);
    return [btnDiv, btn];
}

export function createOptionsDiv() {
    const mainButtonsDiv = document.getElementById('buttons-div');
    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'row d-flex justify-content-center';
    mainButtonsDiv.appendChild(optionsDiv);
    return optionsDiv;
}

export function createNextButton(onNext) {
    const divNext = createOptionsDiv();
    const [btnDiv, btn] = createButton();
    btn.textContent = 'Дальше';
    btn.onclick = onNext;
    divNext.appendChild(btnDiv);
    btn.blur();

    const handler = (e) => {
        if (e.key === 'Enter') {
            document.removeEventListener('keydown', handler);
            onNext();
        }
    };
    document.addEventListener('keydown', handler);
}

export function disableButtons() {
    const trainingDiv = document.getElementById('buttons-div');
    if (!trainingDiv) return;
    trainingDiv.querySelectorAll('button').forEach(btn => { btn.disabled = true; });
}
