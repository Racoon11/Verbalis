let currentWordId = null;

  // Открытие модалки при клике на слово
  document.querySelectorAll('.clickable-word').forEach(word => {
    word.addEventListener('click', () => {
      currentWordId = word.dataset.wordId;
      document.getElementById('modalWordId').value = currentWordId;
      document.getElementById('collectionModal').style.display = 'block';
    });
  });

  // Закрытие модалки
  document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('collectionModal').style.display = 'none';
  });

  // Отправка формы
  document.getElementById('addToCollectionForm').addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    fetch('/words/add-word-to-collection/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'ok') {
        document.getElementById('modalMessage').textContent = 'Слово добавлено!';
        setTimeout(() => {
          document.getElementById('collectionModal').style.display = 'none';
          document.getElementById('modalMessage').textContent = '';
        }, 1500);
      } else {
        alert('Ошибка: ' + data.error);
      }
    });
  });