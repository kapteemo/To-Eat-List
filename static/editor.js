document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('items');
  if (!listEl) return;
  const listId = listEl.dataset.listId;
  const input = document.getElementById('new-item');
  const addBtn = document.getElementById('add-btn');

  function createItemNode(item){
    const li = document.createElement('li');
    li.className = 'item-row';
    li.dataset.id = item.id;

    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = !!item.is_checked;
    cb.className = 'item-cb';

    const span = document.createElement('span');
    span.className = 'item-name';
    span.textContent = item.food_name;
    if (item.is_checked) span.classList.add('completed');

    const del = document.createElement('button');
    del.className = 'item-del';
    del.textContent = '✖';

    li.appendChild(cb);
    li.appendChild(span);
    li.appendChild(del);

    // events
    cb.addEventListener('change', async () => {
      const is_checked = cb.checked ? 1 : 0;
      const res = await fetch('/api/toggle_item', {
        method: 'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({id: item.id, is_checked})
      });
      if (res.ok){
        span.classList.toggle('completed', cb.checked);
      } else {
        cb.checked = !cb.checked;
      }
    });

    del.addEventListener('click', async () => {
      if (!confirm('Delete this item?')) return;
      const res = await fetch('/api/delete_item', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:item.id})});
      if (res.ok){ li.remove(); }
      else { alert('Delete failed'); }
    });

    // double click
    span.addEventListener('dblclick', () => {
      const inp = document.createElement('input');
      inp.type = 'text'; inp.value = span.textContent; inp.className='inline-edit';
      span.replaceWith(inp);
      inp.focus();
      inp.select();
      function finish(){
        const newName = inp.value.trim();
        if (!newName){ inp.replaceWith(span); return; }
        fetch('/api/edit_item', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:item.id, food_name:newName})})
          .then(r=>{ if (r.ok){ span.textContent=newName; inp.replaceWith(span); } else { alert('Edit failed'); inp.replaceWith(span); } });
      }
      inp.addEventListener('blur', finish);
      inp.addEventListener('keydown', (e)=>{ if (e.key==='Enter') finish(); if (e.key==='Escape') inp.replaceWith(span); });
    });

    return li;
  }

  async function loadItems(){
    const res = await fetch(`/api/list_items/${listId}`);
    if (!res.ok) return;
    const items = await res.json();
    listEl.innerHTML = '';
    items.forEach(it => listEl.appendChild(createItemNode(it)));
  }

  addBtn.addEventListener('click', async ()=>{
    const name = input.value.trim();
    if (!name) return;
    const res = await fetch('/api/add_item', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({list_id: parseInt(listId), food_name: name})});
    if (!res.ok){ alert('Add failed'); return; }
    const newItem = await res.json();
    listEl.appendChild(createItemNode(newItem));
    input.value = '';
    input.focus();
  });

  input.addEventListener('keydown', (e)=>{ if (e.key==='Enter'){ addBtn.click(); } });

  // load
  loadItems();
});
