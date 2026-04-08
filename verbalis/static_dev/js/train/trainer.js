import { TranslationExercise } from './exercises/translation.js';
import { SpellingExercise } from './exercises/spelling.js';
import { InputExercise } from './exercises/input.js';
import { updateWords } from './api.js';

// Таблица упражнений: id → фабрика.
// Чтобы добавить новое упражнение:
//   1. Создайте файл в exercises/
//   2. Импортируйте его ниже
//   3. Добавьте строку в EXERCISE_MAP
const EXERCISE_MAP = {
    1: (trainer, word) => new TranslationExercise(trainer, word, 'rus'),
    2: (trainer, word) => new TranslationExercise(trainer, word, 'eng'),
    3: (trainer, word) => new SpellingExercise(trainer, word),
    4: (trainer, word) => new InputExercise(trainer, word),
};

export class VerbalisTrainer {
    constructor(words, order, csrf) {
        this.words = words.map(w => ({
            ...w,
            mistakes: Object.fromEntries(order.map(ex => [ex, 0])),
            progress: 0,
        }));
        this.order = order;
        this.csrf = csrf;
        this.currentWordIndex = 0;
        this.currentExercise = 0;
        this.mainDiv = document.getElementById('train');
    }

    get currentExerciseId() {
        return this.order[this.currentExercise];
    }

    getCurrentWord() {
        return this.words[this.currentWordIndex];
    }

    start() {
        this.render();
    }

    render() {
        this.mainDiv.innerHTML = '';

        if (this.currentWordIndex >= this.words.length) {
            this._finishSession();
            return;
        }

        const word = this.getCurrentWord();
        const factory = EXERCISE_MAP[this.currentExerciseId];

        if (!factory) {
            console.error(`Неизвестный тип упражнения: ${this.currentExerciseId}`);
            this.nextStep();
            return;
        }

        Promise.resolve(factory(this, word).render()).catch(err => {
            console.error('Ошибка при отрисовке упражнения:', err);
        });
    }

    nextStep() {
        this.currentWordIndex = (this.currentWordIndex + 1) % this.words.length;
        if (this.currentWordIndex === 0) {
            this.currentExercise++;
            if (this.currentExercise >= this.order.length) {
                this._finishSession();
                return;
            }
        }
        this.render();
    }

    _finishSession() {
        const wordIds = this.words.map(w => w.id);
        const wordResults = this.words.map(w => {
            const totalMistakes = Object.values(w.mistakes).reduce((sum, m) => sum + m, 0);
            const isCorrect = totalMistakes === 0 || (totalMistakes <= 2 && w.mistakes[2] === totalMistakes);
            return isCorrect ? 0 : 1;
        });
        updateWords(wordIds, wordResults, this.csrf);
        this.mainDiv.innerHTML = '';
        this._renderFinishScreen();
    }

    _renderFinishScreen() {
        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail' style='text-transform: none'> Тренировка закончена! </span>
            </div>
            <div class='row d-flex justify-content-center padding-top'>
                <div class='col-5'><b> Слово </b></div>
                <div class='col-2 d-flex justify-content-end'><b> Ошибки </b></div>
            </div>
            <div id='results-div'></div>
            <div class='row d-flex justify-content-center'>
                <a class='col-6 d-flex justify-content-center no-decoration' href="/training/">
                    <button class='plus-button detail clickable-word train-button'>На главную</button>
                </a>
            </div>
        `;
        this.mainDiv.appendChild(container);

        const resultsDiv = document.getElementById('results-div');
        this.words.forEach(w => {
            const totalMistakes = Object.values(w.mistakes).reduce((sum, m) => sum + m, 0);
            const resultDiv = document.createElement('div');
            resultDiv.className = 'row d-flex justify-content-center';
            resultDiv.innerHTML = `
                <div class='col-5 result-text'>${w.word} - ${w.translation}</div>
                <div class='col-2 d-flex justify-content-end result-text'>${totalMistakes}</div>
            `;
            resultsDiv.appendChild(resultDiv);
        });
    }
}
