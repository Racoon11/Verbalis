export async function getSimilarWords(wordId) {
    const response = await fetch(`/training/get-similar/${wordId}/`);
    if (!response.ok) throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
    const data = await response.json();
    if (!Array.isArray(data.words)) throw new Error('Неверный формат ответа: ожидается массив в поле "words"');
    return data.words;
}

export function updateWords(wordIds, mistakes, csrf) {
    return fetch('/training/update-words/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf,
        },
        body: JSON.stringify({ wordIds, mistakes }),
    });
}
