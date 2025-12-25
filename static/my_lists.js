document.addEventListener('DOMContentLoaded', () => {
  const listsWrap = document.querySelector('.lists-wrap');
  if (!listsWrap) return;

  // Accordion toggle
  listsWrap.addEventListener('click', (e) => {
    const header = e.target.closest('.card-header');
    if (!header) return;

    // Prevent toggle when clicking action buttons
    if (e.target.closest('.icon-btn')) return;

    const card = header.parentElement;
    const toggleBtn = header.querySelector('.list-toggle');
    const isOpen = card.classList.toggle('open');
    if (toggleBtn) toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Edit/delete list and items
  listsWrap.addEventListener('click', async (e) => {
    // Edit list name
    if (e.target.closest('.edit-list')) {
      e.stopPropagation();
      const card = e.target.closest('.list-card');
      const titleEl = card.querySelector('.list-title');
      const current = titleEl.textContent.trim();
      const input = document.createElement('input');
      input.type = 'text';
      input.value = current;
      input.className = 'edit-input';
      titleEl.replaceWith(input);
      input.focus();

      const save = async () => {
        const newName = input.value.trim();
        const listId = card.dataset.listId;
        try {
          const res = await fetch('/api/edit_list', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({list_id: listId, name: newName})
          });
          if (res.ok) {
            const span = document.createElement('span');
            span.className = 'list-title';
            span.textContent = newName || current;
            input.replaceWith(span);
          } else {
            input.replaceWith(titleEl);
          }
        } catch (err) {
          input.replaceWith(titleEl);
        }
      };

      input.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') input.blur();
        if (ev.key === 'Escape') {
          input.replaceWith(titleEl);
        }
      });
      input.addEventListener('blur', save);
      return;
    }

    // Delete list
    if (e.target.closest('.delete-list')) {
      e.stopPropagation();
      const card = e.target.closest('.list-card');
      const listId = card.dataset.listId;
      if (!confirm('Are you sure you want to delete this list?')) return;
      try {
        const res = await fetch('/api/delete_list', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({list_id: listId})
        });
        if (res.ok) card.remove();
      } catch (err) {
        console.error(err);
      }
      return;
    }

    // Edit item
    if (e.target.closest('.edit-item')) {
      e.stopPropagation();
      const row = e.target.closest('.item-row');
      const textEl = row.querySelector('.item-text');
      const current = textEl.textContent.trim();
      const input = document.createElement('input');
      input.type = 'text';
      input.value = current;
      input.className = 'edit-input';
      textEl.replaceWith(input);
      input.focus();

      const saveItem = async () => {
        const newText = input.value.trim();
        const itemId = row.dataset.itemId;
        try {
          const res = await fetch('/api/edit_item', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({id: itemId, food_name: newText})
          });
          if (res.ok) {
            const span = document.createElement('span');
            span.className = 'item-text';
            span.textContent = newText || current;
            input.replaceWith(span);
          } else {
            input.replaceWith(textEl);
          }
        } catch (err) {
          input.replaceWith(textEl);
        }
      };

      input.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter') input.blur();
        if (ev.key === 'Escape') {
          input.replaceWith(textEl);
        }
      });
      input.addEventListener('blur', saveItem);
      return;
    }

    // Delete item
    if (e.target.closest('.delete-item')) {
      e.stopPropagation();
      const row = e.target.closest('.item-row');
      const itemId = row.dataset.itemId;
      if (!confirm('Delete this item?')) return;
      try {
        const res = await fetch('/api/delete_item', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({id: itemId})
        });
        if (res.ok) row.remove();
      } catch (err) {
        console.error(err);
      }
      return;
    }
  });
});
