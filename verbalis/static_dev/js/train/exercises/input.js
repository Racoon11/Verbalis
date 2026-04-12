import { BaseExercise } from './base.js';
import { createButton } from '../ui.js';

export class InputExercise extends BaseExercise {
    render() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail' id='word-to-translate'> ${this.word.translation} </span>
            </div>
            <div class='col-12 d-flex justify-content-center'>
                <input id='word-input' class='train-word-input'></input>
            </div>
            <div id='buttons-div' class='row justify-content-around'></div>
            <div class='train-help-text d-flex justify-content-end'>Перевод слова с русского на английский</div>
        `;
        this.trainer.mainDiv.appendChild(container);

        const buttonsArea = document.getElementById('buttons-div');
        const [btnDiv, btn] = createButton();
        btn.textContent = 'Проверить';
        btn.onclick = () => this._handleAnswer();
        buttonsArea.appendChild(btnDiv);

        const wordInput = document.getElementById('word-input');
        wordInput.focus();

        const checkHandler = (e) => {
            if (e.key === 'Enter' && !wordInput.disabled) {
                document.removeEventListener('keydown', checkHandler);
                this._handleAnswer();
            }
        };
        document.addEventListener('keydown', checkHandler);
    }

    _handleAnswer() {
        const wordInput = document.getElementById('word-input');
        wordInput.disabled = true;

        const entered = wordInput.value.trim();
        if (entered !== this.word.word) {
            this.word.mistakes[this.trainer.currentExerciseId]++;
            wordInput.className += ' ans-wrong';
        } else {
            wordInput.className += ' ans-correct';
        }

        const buttonsArea = document.getElementById('buttons-div');
        buttonsArea.innerHTML = `
            <div class='col-7'>
                ${this.word.sentences && this.word.sentences[0] ? this.word.sentences[0].text : ''}
            </div>
            <div class='col-2'>
                <button id='next-btn' class='plus-button detail clickable-word train-button'
                    style='border-radius: 100%; width: 40px; height: 40px; padding: 0px; text-align: center;'>
                    →
                </button>
            </div>
        `;
        const nextBtn = document.getElementById('next-btn');
        let proceeded = false;
        const proceed = () => {
            if (proceeded) return;
            proceeded = true;
            document.removeEventListener('keydown', handler);
            this.trainer.nextStep();
        };
        nextBtn.onclick = proceed;
        const handler = (e) => {
            if (e.key === 'Enter') proceed();
        };
        document.addEventListener('keydown', handler);

        const wordToTranslate = document.getElementById('word-to-translate');
        wordToTranslate.innerHTML += ` <span>- ${this.word.word}</span>`;
    }
}
