import { VerbalisTrainer } from './train/trainer.js';

const { words, csrf, order } = window.APP_DATA;

const trainer = new VerbalisTrainer(words, order, csrf);
trainer.start();
