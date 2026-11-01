/* Interacciones narrativas independientes del servidor estadístico. */
void (() => {
  const start = () => {
    const body = document.body
    const sidebar = document.querySelector('.sidebar')
    const toggle = document.getElementById('filter-toggle')
    const motion = document.getElementById('motion-toggle')
    let returnFocus = toggle
    const setFilters = open => {
      body.classList.toggle('filters-open', open)
      sidebar.inert = !open
      toggle.setAttribute('aria-expanded', String(open))
      if (open) {
        returnFocus = document.activeElement
        sidebar.querySelector('details').open = true
        document.getElementById('filter-close').focus()
      } else returnFocus.focus()
    }
    toggle.addEventListener('click', () => setFilters(!body.classList.contains('filters-open')))
    document.querySelectorAll('.open-filters').forEach(button => button.addEventListener('click', () => setFilters(true)))
    document.getElementById('filter-close').addEventListener('click', () => setFilters(false))
    document.getElementById('filter-backdrop').addEventListener('click', () => setFilters(false))
    document.addEventListener('keydown', event => {
      if (!body.classList.contains('filters-open')) return
      if (event.key === 'Escape') setFilters(false)
      if (event.key !== 'Tab') return
      const items = Array.from(sidebar.querySelectorAll('button,input,select,summary,a[href],[tabindex="0"]')).filter(item => !item.disabled && item.getClientRects().length)
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault()
        last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault()
        first.focus() }
    })
    const reduced = matchMedia('(prefers-reduced-motion: reduce)')
    let paused = reduced.matches
    const applyMotion = () => {
      body.classList.toggle('motion-paused', paused)
      motion.textContent = paused ? 'Activar movimiento' : 'Pausar movimiento'
      motion.setAttribute('aria-pressed', String(paused))
    }
    applyMotion()
    reduced.addEventListener('change', event => { paused = event.matches
      applyMotion() })
    motion.addEventListener('click', () => { paused = !paused
      applyMotion() })
    const enter = () => document.getElementById('main-content').scrollIntoView({behavior: paused ? 'instant' : 'smooth', block:'start'})
    document.getElementById('begin-expedition').addEventListener('click', enter)
    document.querySelectorAll('[data-page]').forEach(button => button.addEventListener('click', enter))
    const visibility = new IntersectionObserver(entries => entries.forEach(entry => entry.target.classList.toggle('offstage', !entry.isIntersecting)), {threshold:.05})
    document.querySelectorAll('.illustration').forEach(node => visibility.observe(node))
    const metrics = document.getElementById('metrics')
    const update = new MutationObserver(() => {
      metrics.querySelectorAll('.metric').forEach(node => node.classList.add('changed'))
    })
    update.observe(metrics, {childList:true})
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start)
  else start()
})()
/* La trayectoria ilustra la transición del espacio al catálogo terrestre. */
void (() => {
  const setup = () => {
    const hero = document.querySelector('.expedition-hero')
    let scheduled = false
    const move = () => {
      scheduled = false
      if (matchMedia('(prefers-reduced-motion: reduce)').matches || document.body.classList.contains('motion-paused')) return
      const bounds = hero.getBoundingClientRect()
      hero.style.setProperty('--journey', Math.min(1, Math.max(0, -bounds.top / bounds.height)))
    }
    window.addEventListener('scroll', () => {
      if (!scheduled) { scheduled = true
        requestAnimationFrame(move) }
    }, {passive:true})
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup)
  else setup()
})()

