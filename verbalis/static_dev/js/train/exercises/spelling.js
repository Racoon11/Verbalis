import { BaseExercise } from './base.js';
import { createNextButton } from '../ui.js';

export class SpellingExercise extends BaseExercise {
    render() {
        const targetWord = this.word.word;

        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail'> ${this.word.translation} </span>
            </div>
            <div class='row d-flex justify-content-center letters-div' id='letters-div'></div>
            <div class='row d-flex justify-content-center letters-div' id='buttons-div'></div>
            <div class='train-help-text d-flex justify-content-end'>Составление слова по анаграмме</div>
        `;
        this.trainer.mainDiv.appendChild(container);

        const inputArea = document.getElementById('letters-div');
        const buttonsArea = document.getElementById('buttons-div');

        this.word.progress = 0;
        const displaySlots = [];
        const letters = [];

        for (const char of targetWord) {
            if (char === ' ' || char === '-' || char === "'") {
                displaySlots.push(char);
                letters.push(null);
            } else {
                displaySlots.push('_');
                letters.push(char);
            }
        }

        const refreshInputArea = () => {
            inputArea.innerHTML = '';
            displaySlots.forEach(slot => {
                const btn = document.createElement('button');
                btn.className = 'plus-button detail clickable-word letter-button text-letter-button';
                btn.textContent = slot;
                inputArea.appendChild(btn);
            });
        };
        refreshInputArea();

        const letterButtons = letters.filter(l => l !== null).sort(() => Math.random() - 0.5);
        letterButtons.forEach(letter => {
            const btn = document.createElement('button');
            btn.textContent = letter;
            btn.className = 'plus-button detail clickable-word letter-button';
            btn.onclick = () => this._handleLetterClick(btn, targetWord, displaySlots, refreshInputArea, removeKeyListener);
            buttonsArea.appendChild(btn);
        });

        const keyHandler = (e) => {
            if (e.key.length !== 1) return;
            const pressed = e.key.toLowerCase();
            const match = [...buttonsArea.querySelectorAll('button')].find(
                btn => btn.style.display !== 'none' && btn.textContent.toLowerCase() === pressed
            );
            if (match) this._handleLetterClick(match, targetWord, displaySlots, refreshInputArea, removeKeyListener);
        };

        const removeKeyListener = () => document.removeEventListener('keydown', keyHandler);
        document.addEventListener('keydown', keyHandler);
    }

    _handleLetterClick(btn, targetWord, displaySlots, refreshInputArea, removeKeyListener = () => {}) {
        // Пропускаем разделители перед текущей позицией
        while (this.word.progress < displaySlots.length && displaySlots[this.word.progress] !== '_') {
            this.word.progress++;
        }

        if (this.word.progress >= displaySlots.length) return;

        if (btn.textContent === targetWord[this.word.progress]) {
            displaySlots[this.word.progress] = btn.textContent;
            this.word.progress++;

            // Пропускаем разделители после постановки буквы
            while (this.word.progress < displaySlots.length && displaySlots[this.word.progress] !== '_') {
                this.word.progress++;
            }

            refreshInputArea();
            btn.style.display = 'none';

            if (this.word.progress >= targetWord.length) {
                removeKeyListener();
                createNextButton(() => this.trainer.nextStep(), this.word.sentences);
            }
        } else {
            this.word.mistakes[this.trainer.currentExerciseId]++;
            btn.classList.add('ans-wrong');
            void btn.offsetWidth;
            btn.classList.add('shake');
            setTimeout(() => {
                btn.classList.remove('ans-wrong');
                btn.classList.remove('shake');
            }, 600);
        }
    }
}
