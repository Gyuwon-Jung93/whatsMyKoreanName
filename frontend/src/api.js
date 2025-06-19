export async function convertName(name) {
    const res = await fetch('/api/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    });
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    return Array.isArray(data.candidates) ? data.candidates : Array.isArray(data) ? data : [data];
}

export async function saveHistory(englishName, koreanName) {
    return fetch('/api/history/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ englishName, koreanName }),
    }).catch(() => {});
}

export async function deleteHistory(id) {
    if (!id) return;
    return fetch(`/api/history/${id}`, { method: 'DELETE' }).catch(() => {});
}
