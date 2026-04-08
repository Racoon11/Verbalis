import { BaseExercise } from './base.js';
import { getSimilarWords } from '../api.js';
import { shuffleArray } from '../utils.js';
import { createButton, createOptionsDiv, createNextButton, disableButtons } from '../ui.js';

export class TranslationExercise extends BaseExercise {
    // type: 'rus' — показываем английское слово, выбираем русский перевод
    //       'eng' — показываем русский перевод, выбираем английское слово
    constructor(trainer, word, type) {
        super(trainer, word);
        this.type = type;
    }

    async render() {
        const { id, word, translation } = this.word;
        const [displayWord, correctAnswer] = this.type === 'rus'
            ? [word, translation]
            : [translation, word];

        const similarWords = await getSimilarWords(id);
        const distractors = similarWords.map(w => this.type === 'rus' ? w.translation : w.word);
        const options = shuffleArray([correctAnswer, ...distractors]);

        const helpText = this.type === 'rus'
            ? 'Перевод слова с английского на русский'
            : 'Перевод слова с русского на английский';

        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail'> ${displayWord} </span>
            </div>
            <div id='buttons-div'></div>
            <div class='train-help-text d-flex justify-content-end'>${helpText}</div>
        `;
        this.trainer.mainDiv.appendChild(container);

        const digitHandler = (e) => {
            const n = parseInt(e.key);
            if (n >= 1 && n <= options.length) {
                document.removeEventListener('keydown', digitHandler);
                this._handleAnswer(options[n - 1], correctAnswer);
            }
        };
        document.addEventListener('keydown', digitHandler);

        let optionsDiv;
        options.forEach((opt, i) => {
            if (i % 2 === 0) optionsDiv = createOptionsDiv();
            const [btnDiv, btn] = createButton();
            btn.textContent = opt;
            btn.id = opt;
            btn.onclick = () => {
                document.removeEventListener('keydown', digitHandler);
                this._handleAnswer(opt, correctAnswer);
            };
            const badge = document.createElement('span');
            badge.className = 'option-number';
            badge.textContent = i + 1;
            btn.appendChild(badge);
            optionsDiv.appendChild(btnDiv);
        });
    }

    _handleAnswer(chosen, correct) {
        const chBtn = document.getElementById(chosen);
        if (chosen !== correct) {
            this.word.mistakes[this.trainer.currentExerciseId]++;
            chBtn.className += ' ans-wrong';
        } else {
            chBtn.className += ' ans-correct';
        }
        const correctBtn = document.getElementById(correct);
        correctBtn.className += ' ans-correct';
        disableButtons();
        createNextButton(() => this.trainer.nextStep());
    }
}
