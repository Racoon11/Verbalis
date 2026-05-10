import { BaseExercise } from './base.js';
import { createButton } from '../ui.js';
import { checkSentence } from '../api.js';

export class SentenceExercise extends BaseExercise {
    constructor(trainer, word) {
        super(trainer, word);
        this.attempt = 0;
    }

    render() {
        this._renderInput();
    }

    _renderInput(hintMsg = null) {
        this.trainer.mainDiv.innerHTML = '';
        const container = document.createElement('div');
        container.innerHTML = `
            <div class="col-12 d-flex justify-content-center align-items-center gap-2 mb-1">
                <span class="word-title detail">${this._esc(this.word.word)}</span>
                <button id="hint-btn" class="sentence-hint-btn" title="Показать перевод">💡</button>
            </div>
            <div id="translation-hint" class="sentence-translation-hint" style="display:none;">
                ${this._esc(this.word.translation)}
            </div>
            ${hintMsg ? `<div class="sentence-retry-msg">${hintMsg}</div>` : ''}
            <div class="col-12 d-flex justify-content-center mt-3">
                <textarea id="sentence-input" class="sentence-input" rows="2"
                    placeholder='Составьте предложение со словом "${this._esc(this.word.word)}"'></textarea>
            </div>
            <div id="buttons-div" class="row justify-content-around"></div>
            <div class="train-help-text d-flex justify-content-end">Составьте предложение с указанным словом</div>
        `;
        this.trainer.mainDiv.appendChild(container);

        document.getElementById('hint-btn').onclick = () => {
            const hint = document.getElementById('translation-hint');
            hint.style.display = hint.style.display === 'none' ? 'block' : 'none';
        };

        const buttonsArea = document.getElementById('buttons-div');
        const [btnDiv, btn] = createButton();
        btn.textContent = 'Проверить';
        btn.onclick = () => this._submit();
        buttonsArea.appendChild(btnDiv);

        const input = document.getElementById('sentence-input');
        input.focus();

        const handler = (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !input.disabled) {
                e.preventDefault();
                document.removeEventListener('keydown', handler);
                this._submit();
            }
        };
        document.addEventListener('keydown', handler);
    }

    async _submit() {
        const input = document.getElementById('sentence-input');
        if (!input) return;
        const sentence = input.value.trim();
        if (!sentence) return;

        if (sentence.split(/\s+/).length < 3) {
            this._renderInput('Предложение слишком короткое — используйте хотя бы три слова');
            return;
        }

        input.disabled = true;
        const btn = document.querySelector('#buttons-div button');
        if (btn) btn.disabled = true;

        this.attempt++;
        try {
            const result = await checkSentence(this.word.word, sentence, this.trainer.csrf);
            this._showResult(sentence, result);
        } catch {
            this._proceed();
        }
    }

    _showResult(sentence, result) {
        this.trainer.mainDiv.innerHTML = '';
        const container = document.createElement('div');

        const errors = result.errors || [];
        const highlighted = this._highlight(sentence, errors);

        // Positive feedback when sentence is fully correct
        const okMsg = result.is_correct && result.word_found
            ? `<div class="sentence-ok-msg">Отлично!</div>`
            : '';

        const correctedLine = result.corrected_sentence && result.corrected_sentence !== sentence
            ? `<div class="sentence-corrected">→ ${this._esc(result.corrected_sentence)}</div>`
            : '';

        const needRetry = !result.word_found && this.attempt < 2;
        // If the target word itself was misspelled, LanguageTool will suggest it as a replacement
        const wordMisspelled = this._wordMisspelled(errors);
        // Show "word not found" only when it's truly absent (not just misspelled)
        const retryMsg = needRetry && !wordMisspelled
            ? `<div class="sentence-retry-msg">Слово <b>${this._esc(this.word.word)}</b> не найдено — попробуйте ещё раз</div>`
            : '';

        container.innerHTML = `
            <div class="col-12 d-flex justify-content-center mb-2">
                <span class="word-title detail">${this._esc(this.word.word)}</span>
            </div>
            <div class="sentence-result-block">
                ${okMsg}
                <div class="sentence-user">${highlighted}</div>
                ${correctedLine}
                ${retryMsg}
            </div>
            <div id="buttons-div" class="row justify-content-around mt-3"></div>
        `;
        this.trainer.mainDiv.appendChild(container);

        const buttonsArea = document.getElementById('buttons-div');

        if (needRetry) {
            const [btnDiv, btn] = createButton();
            btn.textContent = 'Попробовать снова';
            // If word was misspelled — no extra hint (errors already highlighted above)
            // If word was truly absent — remind the user to include it
            const retryHint = wordMisspelled
                ? null
                : `Используйте слово <b>${this._esc(this.word.word)}</b> в предложении`;
            btn.onclick = () => this._renderInput(retryHint);
            buttonsArea.appendChild(btnDiv);
        } else {
            const nextDiv = document.createElement('div');
            nextDiv.className = 'col-2 d-flex justify-content-center';
            nextDiv.innerHTML = `<button id="next-btn" class="plus-button detail clickable-word train-button"
                style="border-radius:100%;width:40px;height:40px;padding:0;text-align:center;">→</button>`;
            buttonsArea.appendChild(nextDiv);

            let done = false;
            const proceed = () => {
                if (done) return;
                done = true;
                document.removeEventListener('keydown', handler);
                this._proceed();
            };
            document.getElementById('next-btn').onclick = proceed;
            const handler = (e) => { if (e.key === 'Enter') proceed(); };
            document.addEventListener('keydown', handler);
        }
    }

    _wordMisspelled(errors) {
        const target = this.word.word.toLowerCase();
        return errors.some(e => e.replacements.some(r => r.toLowerCase() === target));
    }

    _highlight(sentence, errors) {
        if (!errors.length) return this._esc(sentence);
        const sorted = [...errors].sort((a, b) => a.offset - b.offset);
        let out = '';
        let pos = 0;
        for (const err of sorted) {
            out += this._esc(sentence.slice(pos, err.offset));
            out += `<span class="sentence-error">${this._esc(sentence.slice(err.offset, err.offset + err.length))}</span>`;
            pos = err.offset + err.length;
        }
        out += this._esc(sentence.slice(pos));
        return out;
    }

    _esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    _proceed() {
        this.trainer.nextStep();
    }
}
