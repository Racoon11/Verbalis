const { userId, words } = window.APP_DATA;

console.log("Пользователь ID:", userId);
console.log(words);

class VerbalisTrianer {
    constructor(words, order) {
        this.words = words.map(w => ({
            ...w,
            mistakes: [0, 0, 0, 0], // fix, len(order)
            progress: 0
        }));
        this.order = order;
        this.currentWordIndex = 0;
        this.currentExercise = order[0];
        this.totalExercises = this.order.length; // len(order)
        this.mainDiv = document.getElementById('train');
    }

    getCurrentWord() {
        return this.words[this.currentWordIndex];
    }

    start() {
        this.render();
    }

    render() {
        this.clearScreen();
        if (this.currentWordIndex >= this.words.length) {
            this.finishSession();
            return;
        }

        const word = this.getCurrentWord();
        switch (this.currentExercise) {
            case 0:
                this.renderTranslation(word.id, word.word, word.translation, 'rus');
                break;
            case 1:
                this.renderTranslation(word.id, word.translation, word.word, 'eng');
                break;
            case 2:
                this.renderSpelling(word);
                break;
            case 3:
                this.renderInput(word);
                break;
        }
    }

    clearScreen() {
        this.mainDiv.innerHTML = '';
    }

    async getSimilarWords(wordId) {
        try {
            const response = await fetch(`/training/get-similar/${wordId}/`);

            if (!response.ok) {
                throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
            }

            const data = await response.json(); // ожидаем JSON вида { words: [...] }

            // Проверяем структуру ответа
            if (!Array.isArray(data.words)) {
                throw new Error('Неверный формат ответа: ожидается массив в поле "words"');
            }
            return data.words; // массив объектов: [{id: 1, word: "...", translation: "..."}, ...]
        } catch (error) {
            console.error('Не удалось загрузить слова:', error);
            throw error; // чтобы вызывающий код мог обработать ошибку
        }
    }
    
    shuffleArray(array) {
        const shuffled = [...array]; // создаём копию, чтобы не менять оригинал
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; // обмен значениями
        }
        return shuffled;
    }

    async renderTranslation(id, word, translation, type) {
        const words = await this.getSimilarWords(id);
        let options = [translation];
        words.forEach(w => {
            if (type === 'rus') { 
                options.push(w.translation);
            } else {
                options.push(w.word);
            }
        });

        options = this.shuffleArray(options);

        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail'> ${word} </span>
            </div>

            <div id='buttons-div'>
            </div>

            <div class='train-help-text d-flex justify-content-end'>
                Перевод слова с английского на русский
            </div>
        `
        this.mainDiv.appendChild(container);
        let i = 0;
        let optionsDiv;
        options.forEach(opt => {
            if (i % 2 === 0) {
                optionsDiv = this.createOptionsDiv();
            }
            const [btnDiv, btn] = this.createButton();
            btn.textContent = opt;
            btn.id = opt;
            btn.onclick = () => this.handleTranslateAnswer(opt, translation);
            optionsDiv.appendChild(btnDiv);
            i++;
        });
    }

    createButton() {
        const btnDiv = document.createElement('div');
        btnDiv.className = 'col-6 d-flex justify-content-center';
        const btn = document.createElement('button');
        btn.className = 'plus-button detail clickable-word train-button';
        btnDiv.appendChild(btn);
        return [btnDiv, btn];
    }

    createOptionsDiv() {
        const mainButtonsDiv = document.getElementById('buttons-div');
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'row d-flex justify-content-center'
        mainButtonsDiv.appendChild(optionsDiv);
        return optionsDiv;
    }

    createNextButton() {
        const divNext = this.createOptionsDiv();
        const [btnDiv, btn] = this.createButton();
        btn.textContent = 'Дальше';
        btn.onclick = () => this.nextStep();
        divNext.appendChild(btnDiv);
    }

    disableButtons() {
        const trainingDiv = document.getElementById('buttons-div');
        if (!trainingDiv) return; // если элемент не найден — выходим

        const buttons = trainingDiv.querySelectorAll('button');
        buttons.forEach(button => {
            button.disabled = true;
        });
    }

    handleTranslateAnswer(chosen, correct) {
        const chBtn = document.getElementById(chosen);
        if (!(chosen === correct)) {
            this.getCurrentWord().mistakes[this.currentExercise]++;
            chBtn.className += ' ans-wrong';
        } else {
            chBtn.className += ' ans-correct';
        }
        this.disableButtons();

        this.createNextButton();
    }

    renderSpelling(word) {
        const targetWord = word.word;
        const container = document.createElement('div');
        container.innerHTML = `
            <div class='col-12 d-flex justify-content-center'>
                <span class='word-title detail'> ${word.translation} </span>
            </div>
            
                <div class='row d-flex justify-content-center letters-div' id='letters-div'>
                </div>
                <div class='row d-flex justify-content-center letters-div'  id='buttons-div'>
                </div>
            <div id='buttons-div'>
            </div>

            <div class='train-help-text d-flex justify-content-end'>
                Составление слова по анаграмме
            </div>
        `
        this.mainDiv.appendChild(container);

        const inputArea = document.getElementById('letters-div');
        const buttonsArea = document.getElementById('buttons-div');

        word.progress = 0;
        const letters = [];
        const displaySlots = []; // то, что показываем пользователю как "пустые места"

        for (let char of targetWord) {
            if (char === ' ' || char === '-' || char === "'") {
                displaySlots.push(char);
                letters.push(null); // метка для разделителя
            } else {
                displaySlots.push('_');
                letters.push(char);
            }
        }
        const refreshInputArea = () => {
            inputArea.innerHTML = '';
            displaySlots.forEach((slot, i) => {
                const btn = document.createElement('button');
                btn.className = 'plus-button detail clickable-word letter-button text-letter-button'
                if (typeof slot === 'string' && slot !== '_') {
                    btn.textContent = slot;
                } else {
                    btn.textContent = slot;
                }
                inputArea.appendChild(btn);
            });
        };
        refreshInputArea();

        const letterButtons = letters.filter(l => l !== null).sort(() => Math.random() - 0.5);
        letterButtons.forEach((letter) => {
            const btn = document.createElement('button');
            btn.textContent = letter;
            btn.className = 'plus-button detail clickable-word letter-button';

            btn.onclick = () => {
                const currentPos = word.progress;
                if (currentPos >= displaySlots.length) return;

                // Пропускаем разделители
                while (currentPos < displaySlots.length && displaySlots[currentPos] !== '_') {
                    word.progress++;
                }

                if (word.progress >= displaySlots.length) return;

                if (btn.textContent === targetWord[word.progress]) {
                    // Правильная буква
                    displaySlots[word.progress] = btn.textContent;
                    word.progress++;
                    refreshInputArea();
                    btn.style.display = 'none';

                    // Проверка завершения
                    if (word.progress >= targetWord.length) {
                        this.createNextButton();
                    }
                } else {
                    // Ошибка
                    word.mistakes[this.currentExercise]++;
                    console.log(word.mistakes);
                    btn.classList.add('ans-wrong');
                    
                    void btn.offsetWidth;
                    btn.classList.add('shake');
                    setTimeout(() => {
                        btn.classList.remove('ans-wrong');
                        btn.classList.remove('shake');
                    }, 600);
                }
            };
            buttonsArea.appendChild(btn);
        });
    }

    renderInput(word) {
        
    }

    nextStep() {
        this.currentWordIndex = (this.currentWordIndex + 1) % this.words.length;
        if (this.currentWordIndex === 0) {
            this.currentExercise++;
        }
        this.render();
    }
}

const trainer = new VerbalisTrianer(words, [0, 2, 1, 3]);
trainer.start();