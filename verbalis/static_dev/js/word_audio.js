/**
 * Воспроизведение произношения слова через Web Speech API.
 * Кнопки должны иметь атрибуты data-word и data-lang.
 */

const LANG_MAP = {
  'english':    'en-US',
  'french':     'fr-FR',
  'german':     'de-DE',
  'spanish':    'es-ES',
  'italian':    'it-IT',
  'portuguese': 'pt-PT',
  'chinese':    'zh-CN',
  'japanese':   'ja-JP',
  'korean':     'ko-KR',
  'arabic':     'ar-SA',
  'dutch':      'nl-NL',
  'polish':     'pl-PL',
  'turkish':    'tr-TR',
  'swedish':    'sv-SE',
};

function speakWord(word, langSlug) {
  if (!window.speechSynthesis) return;

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(word);
  utterance.lang = LANG_MAP[langSlug] || langSlug || 'en-US';
  utterance.rate = 0.9;

  window.speechSynthesis.speak(utterance);
}

document.addEventListener('click', function (e) {
  const btn = e.target.closest('[data-word]');
  if (!btn) return;

  const word = btn.dataset.word;
  const lang = btn.dataset.lang || '';
  speakWord(word, lang);
});
