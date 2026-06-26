document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('search-form');
    const results = document.getElementById('search-results');
    if (!form || !results) return;

    let debounceTimer;
    const doSearch = () => {
        const params = new URLSearchParams(new FormData(form));
        fetch(`${window.location.pathname}?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(data => { results.innerHTML = data.html; })
        .catch(() => {});
    };

    form.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(doSearch, 300);
        });
        el.addEventListener('change', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(doSearch, 300);
        });
    });
});
