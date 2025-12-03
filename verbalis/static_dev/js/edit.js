document.addEventListener('DOMContentLoaded', () => {
  const puzzleZone = document.getElementById('puzzleZone');
  const addBtn = document.getElementById('addPuzzleBtn');
  const template = document.getElementById('puzzleTemplate');
  let puzzleCounter = 1;

  // --- Добавление пазла ---
  addBtn.addEventListener('click', () => {
    const clone = template.content.cloneNode(true);
    const img = clone.querySelector('img');
    img.dataset.id = puzzleCounter;
    img.src = img.src.replace('?', puzzleCounter);
    puzzleCounter++;

    const draggable = img;
    draggable.addEventListener('dragstart', dragStart);
    draggable.addEventListener('dragend', dragEnd);

    puzzleZone.appendChild(draggable);
  });

  // --- Drag & Drop внутри зоны ---
  function dragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
    e.target.classList.add('dragging');
  }

  function dragEnd(e) {
    e.target.classList.remove('dragging');
  }

  puzzleZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    const afterElement = getDragAfterElement(puzzleZone, e.clientX);
    const draggable = document.querySelector('.dragging');

    if (afterElement == null) {
      puzzleZone.appendChild(draggable);
    } else {
      puzzleZone.insertBefore(draggable, afterElement);
    }
  });

  function getDragAfterElement(container, x) {
    const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = x - box.left - box.width / 2;

      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }
});