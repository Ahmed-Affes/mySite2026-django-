/**
 * MyMagasin — Theme Manager  v2.0
 * Handles dark / light mode toggle, persistence via localStorage,
 * system preference detection, and chart colour updates.
 */
class ThemeManager {
  constructor() {
    // Prefer saved choice, fall back to system preference
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.theme = saved || (prefersDark ? 'dark' : 'light');
    this._apply();
    this._setupSystemListener();
  }

  /** Apply theme to <html> and update the toggle icon */
  _apply() {
    document.documentElement.setAttribute('data-theme', this.theme);
    this._updateIcon();
  }

  toggle() {
    this.theme = this.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', this.theme);
    this._apply();
    this._updateCharts();
    if (typeof showToast === 'function') {
      showToast(
        this.theme === 'light' ? '☀️ Mode clair activé' : '🌙 Mode sombre activé',
        'info'
      );
    }
  }

  setTheme(t) {
    if (t !== 'light' && t !== 'dark') return;
    this.theme = t;
    localStorage.setItem('theme', t);
    this._apply();
    this._updateCharts();
  }

  _updateIcon() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    const icon = btn.querySelector('i');
    if (icon) icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    btn.setAttribute(
      'aria-label',
      this.theme === 'light' ? 'Passer en mode sombre' : 'Passer en mode clair'
    );
  }

  _setupSystemListener() {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      // Only react if the user hasn't explicitly chosen a theme
      if (!localStorage.getItem('theme')) {
        this.theme = e.matches ? 'dark' : 'light';
        this._apply();
      }
    });
  }

  /** Re-colour Chart.js instances when theme changes */
  _updateCharts() {
    const isDark    = this.theme === 'dark';
    const textColor = isDark ? '#E5E7EB' : '#1A202C';
    const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';

    [window.salesChart, window.categoryChart].forEach((chart) => {
      if (!chart) return;

      // Scales (line/bar charts)
      if (chart.options.scales) {
        ['x', 'y'].forEach((axis) => {
          if (chart.options.scales[axis]) {
            if (chart.options.scales[axis].grid)
              chart.options.scales[axis].grid.color = gridColor;
            if (chart.options.scales[axis].ticks)
              chart.options.scales[axis].ticks.color = textColor;
          }
        });
      }

      // Legend (doughnut / pie)
      if (chart.options.plugins?.legend?.labels)
        chart.options.plugins.legend.labels.color = textColor;

      chart.update();
    });
  }
}

// ── Bootstrap ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();

  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => window.themeManager.toggle());
  }
});