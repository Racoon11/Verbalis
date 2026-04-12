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

export function createNextButton(onNext, sentences = null) {
    const divNext = createOptionsDiv();
    divNext.className = 'row d-flex justify-content-start align-items-center px-3';

    const sentenceDiv = document.createElement('div');
    sentenceDiv.className = 'col-9';
    sentenceDiv.textContent = sentences && sentences[0] ? sentences[0].text : '';
    divNext.appendChild(sentenceDiv);

    const [btnDiv, btn] = createButton();
    btnDiv.className = 'col-2 d-flex justify-content-center';
    btn.id = 'next-btn';
    btn.textContent = '→';
    btn.style.cssText = 'border-radius: 100%; width: 40px; height: 40px; padding: 0px; text-align: center;';
    divNext.appendChild(btnDiv);
    btn.blur();

    let proceeded = false;
    const proceed = () => {
        if (proceeded) return;
        proceeded = true;
        document.removeEventListener('keydown', handler);
        onNext();
    };
    btn.onclick = proceed;

    const handler = (e) => {
        if (e.key === 'Enter') proceed();
    };
    document.addEventListener('keydown', handler);
}

export function disableButtons() {
    const trainingDiv = document.getElementById('buttons-div');
    if (!trainingDiv) return;
    trainingDiv.querySelectorAll('button').forEach(btn => { btn.disabled = true; });
}
