document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.countdown').forEach(el => {
        let seconds = parseInt(el.dataset.seconds, 10);
        const btn = el.closest('tr')?.querySelector('.cancel-btn');
        const tick = () => {
            if (seconds <= 0) {
                el.textContent = 'مهلت لغو به پایان رسید';
                if (btn) { btn.disabled = true; btn.classList.add('disabled'); }
                return;
            }
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = seconds % 60;
            el.textContent = `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
            seconds--;
            setTimeout(tick, 1000);
        };
        tick();
    });
});
