let selectedConditions = new Set();

async function loadConditions() {
  const box = document.getElementById('conditions');
  try {
    const res = await fetch('/api/conditions');
    if (!res.ok) throw new Error('Could not load health conditions.');

    const conditions = await res.json();
    box.innerHTML = '';

    if (!conditions.length) {
      box.innerHTML = '<p>No health conditions are available.</p>';
      return;
    }

    conditions.forEach(c => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'condition';
      btn.textContent = c.name;
      btn.onclick = () => {
        if (selectedConditions.has(c.id)) {
          selectedConditions.delete(c.id);
          btn.classList.remove('selected');
        } else {
          selectedConditions.add(c.id);
          btn.classList.add('selected');
        }
      };
      box.appendChild(btn);
    });
  } catch (err) {
    box.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

async function analyze() {
  const text = document.getElementById('ingredients').value.trim();
  if (!text) return alert('Please enter ingredients.');

  const button = document.getElementById('analyzeBtn');
  button.disabled = true;
  button.textContent = 'Analyzing...';

  try {
    const ingredients = text.split(',').map(x => x.trim()).filter(Boolean);
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        conditions: Array.from(selectedConditions),
        ingredients
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Analysis failed');

    showResult(data);
    await loadHistory();
  } catch (err) {
    alert(err.message);
  } finally {
    button.disabled = false;
    button.textContent = 'Analyze Safety Risks';
  }
}

function showResult(data) {
  const box = document.getElementById('result');
  box.classList.remove('hidden');

  let html = `<h2>3. Analysis Result</h2><div class="score">${data.safety_score}/100</div><h3>${data.status}</h3>`;

  if (data.flagged_ingredients.length) {
    html += '<h3>Flagged Ingredients</h3>';
    data.flagged_ingredients.forEach(item => {
      html += `<div class="alert"><b>${escapeHtml(item.ingredient)}</b> → ${escapeHtml(item.condition_triggered)}<br>${escapeHtml(item.warning)}</div>`;
    });
  } else {
    html += '<div class="safe">No matching high-risk ingredients were found for the selected conditions.</div>';
  }

  const substitutions = Object.entries(data.suggested_substitutions);
  if (substitutions.length) {
    html += '<h3>Suggested Substitutions</h3><ul>';
    substitutions.forEach(([from, to]) => {
      html += `<li><b>${escapeHtml(from)}</b> → ${escapeHtml(to)}</li>`;
    });
    html += '</ul>';
  }

  box.innerHTML = html;
  box.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

async function loadHistory() {
  const box = document.getElementById('history');
  try {
    const res = await fetch('/api/history');
    if (!res.ok) throw new Error('Could not load history.');

    const rows = await res.json();
    if (!rows.length) {
      box.textContent = 'No analyses saved yet.';
      return;
    }

    box.innerHTML = rows.map(row => `
      <div class="history-row">
        <b>${escapeHtml(row.status)} — ${row.safety_score}/100</b><br>
        <small>Conditions: ${escapeHtml(row.conditions.join(', ') || 'None')}<br>${new Date(row.created_at).toLocaleString()}</small>
      </div>
    `).join('');
  } catch (err) {
    box.innerHTML = `<p class="error">${err.message}</p>`;
  }
}

loadConditions();
loadHistory();
