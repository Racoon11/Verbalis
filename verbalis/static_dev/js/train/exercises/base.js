export class BaseExercise {
    constructor(trainer, word) {
        this.trainer = trainer;
        this.word = word;
    }

    // Должен вернуть void или Promise<void>
    render() {
        throw new Error('render() must be implemented by subclass');
    }
}
