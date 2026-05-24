(function () {
    'use strict';

    function isDark() {
        return document.documentElement.classList.contains('dark');
    }

    function applyTheme(dark) {
        document.documentElement.classList.toggle('dark', dark);
        document.documentElement.classList.toggle('light', !dark);
        var btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
            btn.textContent = dark ? '☀' : '☽';
        }
    }

    function toggleTheme() {
        var nowDark = !isDark();
        localStorage.setItem('theme', nowDark ? 'dark' : 'light');
        applyTheme(nowDark);
        if (typeof window.calculate === 'function') window.calculate();
    }

    window.getChartColors = function () {
        var dark = isDark();
        return {
            grid: dark ? '#374151' : '#e5e7eb',
            tick: dark ? '#9ca3af' : '#6b7280',
            legend: dark ? '#f9fafb' : '#111827',
            tooltipBg: dark ? '#1f2937' : '#ffffff',
            tooltipText: dark ? '#f9fafb' : '#111827',
            tooltipBorder: dark ? '#374151' : '#e5e7eb',
            startLine: dark ? '#4b5563' : '#d1d5db',
            contribLine: dark ? '#6b7280' : '#9ca3af',
        };
    };

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches);
            if (typeof window.calculate === 'function') window.calculate();
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        var nav = document.querySelector('header nav') || document.querySelector('header .inner');
        if (!nav) return;

        var btn = document.createElement('button');
        btn.id = 'theme-toggle';
        btn.className = 'theme-toggle';
        btn.setAttribute('aria-label', isDark() ? 'Switch to light mode' : 'Switch to dark mode');
        btn.textContent = isDark() ? '☀' : '☽';
        btn.addEventListener('click', toggleTheme);

        nav.appendChild(btn);
    });
})();
