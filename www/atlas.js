/* Puente reactivo de Shiny con Plotly y un mapa local de Leaflet. */
(() => {
  'use strict'
  let map
  let marks
  let rows = []
  let mode = 'points'
  let mapVersion = 0
  const colors = { Found: '#42d7ae', Fell: '#ffb35f' }
  const fmt = new Intl.NumberFormat('es-CR', { maximumFractionDigits: 2 })
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const escape = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]))
  const readable = value => value == null ? 'No informado' : fmt.format(value)
  const condition = value => value === 'Fell' ? 'Caída observada' : 'Hallazgo'

  function popup(row) {
    return `<div class="popup-kicker">${condition(row[3])}</div>
      <div class="popup-title">${escape(row[0])}</div>
      <div class="popup-grid">
      <div><small>CLASIFICACIÓN</small><strong>${escape(row[1])}</strong></div>
      <div><small>MASA</small><strong>${readable(row[2])}${row[2] == null ? '' : ' g'}</strong></div>
      <div><small>AÑO DEL CATÁLOGO</small><strong>${row[4] == null ? 'No informado' : row[4]}${row[4] > 2013 ? ' · anómalo' : ''}</strong></div>
      <div><small>COORDENADAS</small><strong>${fmt.format(row[5])}°, ${fmt.format(row[6])}°</strong></div>
      </div><p class="popup-note">${row[3] === 'Found' ? 'El año indica el hallazgo, no una fecha conocida de impacto.' : 'El catálogo registra una caída observada.'}</p>`
  }

  function renderPoints() {
    if (!map || !marks) return
    marks.clearLayers()
    const viewport = map.getBounds().pad(0.1)
    const cells = new Map()
    const zoom = map.getZoom()
    const size = 54
    for (const row of rows) {
      if (!viewport.contains([row[5], row[6]])) continue
      const pixel = map.project([row[5], row[6]], zoom)
      const key = `${Math.floor(pixel.x / size)},${Math.floor(pixel.y / size)}`
      let group = cells.get(key)
      if (!group) {
        group = { items: [], lat: 0, lon: 0, fell: 0 }
        cells.set(key, group)
      }
      group.items.push(row)
      group.lat += row[5]
      group.lon += row[6]
      group.fell += row[3] === 'Fell' ? 1 : 0
    }
    for (const group of cells.values()) {
      const n = group.items.length
      if (n === 1) {
        const row = group.items[0]
        const mass = row[2]
        const radius = mass == null || mass <= 0 ? 4 : Math.min(15, 4 + Math.log10(1 + mass) * 1.25)
        const marker = L.circleMarker([row[5], row[6]], {
          radius, color: colors[row[3]], weight: 1, fillColor: colors[row[3]], fillOpacity: .65,
        }).addTo(marks)
        marker.bindPopup(popup(row), { maxWidth: 330 })
        marker.bindTooltip(`${escape(row[0])} · ${readable(mass)}${mass == null ? '' : ' g'}`)
      } else {
        const color = group.fell === n ? colors.Fell : group.fell === 0 ? colors.Found : '#b4a2fb'
        const marker = L.circleMarker([group.lat / n, group.lon / n], {
          radius: Math.min(28, 11 + Math.log10(n) * 4), color, weight: 1.2, fillColor: color, fillOpacity: .22,
        }).addTo(marks)
        marker.bindTooltip(fmt.format(n), { permanent: true, direction: 'center', className: 'cluster-count' })
        marker.on('click', () => {
          const bounds = L.latLngBounds(group.items.map(row => [row[5], row[6]]))
          if (zoom < 8 && (bounds.getNorth() - bounds.getSouth() > .001 || bounds.getEast() - bounds.getWest() > .001)) {
            map.fitBounds(bounds, { padding: [45, 45], maxZoom: Math.min(zoom + 3, 9), animate: !reducedMotion })
          } else {
            marker.bindPopup(`<div class="popup-kicker">Ubicaciones próximas</div><div class="popup-title">${fmt.format(n)} registros</div>
              <p class="popup-note">${fmt.format(n - group.fell)} hallazgos · ${fmt.format(group.fell)} caídas observadas</p>
              ${group.items.slice(0, 5).map(row => `<div>${escape(row[0])} · ${readable(row[2])} g</div>`).join('')}
              <p class="popup-note">${n > 5 ? 'Se muestran los primeros 5 nombres. ' : ''}Buscá un nombre en el filtro general para explorar su ficha individual.</p>`).openPopup()
          }
        })
      }
    }
    document.getElementById('atlas-map').dataset.visibleGroups = cells.size
  }

  function renderConcentration() {
    if (!marks) return
    marks.clearLayers()
    const cells = new Map()
    for (const row of rows) {
      const lat = Math.min(85, Math.floor(row[5] / 5) * 5)
      const lon = Math.min(175, Math.floor(row[6] / 5) * 5)
      const key = `${lat},${lon}`
      if (!cells.has(key)) cells.set(key, { lat, lon, count: 0, fell: 0 })
      const cell = cells.get(key)
      cell.count++
      cell.fell += row[3] === 'Fell' ? 1 : 0
    }
    const max = Math.max(1, ...Array.from(cells.values()).map(cell => cell.count))
    for (const cell of cells.values()) {
      const strength = Math.log1p(cell.count) / Math.log1p(max)
      L.rectangle([[cell.lat, cell.lon], [cell.lat + 5, cell.lon + 5]], {
        color: '#b4a2fb', weight: .5, opacity: .4, fillColor: '#b4a2fb', fillOpacity: .12 + .73 * strength,
      }).addTo(marks).bindTooltip(`${fmt.format(cell.count)} registros · celda de 5° × 5°`).bindPopup(
        `<div class="popup-kicker">Concentración del catálogo</div><div class="popup-title">${fmt.format(cell.count)} registros</div>
        <div>${fmt.format(cell.count - cell.fell)} hallazgos · ${fmt.format(cell.fell)} caídas observadas</div>
        <p class="popup-note">Latitud ${cell.lat}° a ${cell.lat + 5}° · Longitud ${cell.lon}° a ${cell.lon + 5}°<br>Conteo por celda angular, no densidad por km². Las celdas no tienen igual superficie terrestre.</p>`)
    }
    document.getElementById('atlas-map').dataset.visibleGroups = cells.size
  }

  function redraw() {
    if (mode === 'concentration') renderConcentration()
    else renderPoints()
  }

  function initMap() {
    map = L.map('atlas-map', {
      crs: L.CRS.EPSG4326, preferCanvas: true, minZoom: -2, maxZoom: 10, zoomSnap: .25,
      zoomAnimation: !reducedMotion, fadeAnimation: !reducedMotion, markerZoomAnimation: !reducedMotion,
      scrollWheelZoom: false, maxBounds: [[-105, -220], [105, 220]], maxBoundsViscosity: .6,
    })
    map.attributionControl.setPrefix('Leaflet')
    map.attributionControl.addAttribution('Natural Earth · NASA / The Meteoritical Society')
    map.zoomControl.setPosition('bottomright')
    document.querySelector('.leaflet-control-zoom-in').setAttribute('aria-label', 'Acercar mapa')
    document.querySelector('.leaflet-control-zoom-out').setAttribute('aria-label', 'Alejar mapa')
    map.fitBounds([[-90, -180], [90, 180]], { padding: [10, 10], animate: false })
    for (let lat = -60; lat <= 60; lat += 30) {
      L.polyline([[lat, -180], [lat, 180]], { color: '#31516b', weight: .6, opacity: .35, interactive: false }).addTo(map)
    }
    for (let lon = -180; lon <= 180; lon += 30) {
      L.polyline([[-90, lon], [90, lon]], { color: '#31516b', weight: .6, opacity: .35, interactive: false }).addTo(map)
    }
    marks = L.layerGroup().addTo(map)
    fetch('vendor/world.geojson').then(response => {
      if (!response.ok) throw new Error('Cartografía no disponible')
      return response.json()
    }).then(geo => {
      L.geoJSON(geo, { style: { color: '#72a292', weight: .65, fillColor: '#315a67', fillOpacity: .8 }, interactive: false }).addTo(map).bringToBack()
      document.getElementById('atlas-map').dataset.basemap = 'ready'
    }).catch(() => {
      map.attributionControl.addAttribution('Mapa base no disponible, se muestran coordenadas')
    })
    map.on('moveend', redraw)
    document.getElementById('world-view').addEventListener('click', () => map.fitBounds([[-90, -180], [90, 180]], { animate: !reducedMotion }))
    redraw()
  }

  function init() {
    if (window.locale) Plotly.register({ ...window.locale, dictionary: {
      ...window.locale.dictionary,
      'Download plot as a PNG': 'Descargar gráfico como PNG',
      'Download plot as PNG': 'Descargar gráfico como PNG',
      'Image download succeeded': 'Imagen descargada',
      'Taking snapshot - this may take a few seconds': 'Preparando imagen, puede tardar unos segundos',
      'Sorry, there was a problem downloading your image!': 'No se pudo descargar la imagen. Intentá de nuevo.',
    } })
    const details = document.querySelector('.sidebar details')
    details.open = true
    document.querySelectorAll('[data-page]').forEach(button => {
      button.addEventListener('click', () => {
        document.querySelectorAll('[data-page]').forEach(item => {
          item.classList.toggle('active', item === button)
          item.setAttribute('aria-pressed', item === button ? 'true' : 'false')
        })
        document.querySelectorAll('.atlas-page').forEach(page => page.classList.toggle('active', page.id === `page-${button.dataset.page}`))
        if (map) map.invalidateSize()
        document.querySelectorAll('.plot').forEach(plot => {
          if (plot.data && plot.offsetWidth > 0) Plotly.Plots.resize(plot)
        })
      })
    })
    initMap()
    const resize = new ResizeObserver(() => {
      document.querySelectorAll('.plot').forEach(plot => {
        if (plot.data && plot.offsetWidth > 0) Plotly.Plots.resize(plot)
      })
      map.invalidateSize()
    })
    resize.observe(document.getElementById('main-content'))
    Shiny.addCustomMessageHandler('atlas-map', payload => {
      rows = payload.rows
      mode = payload.mode
      mapVersion++
      const element = document.getElementById('atlas-map')
      element.dataset.records = rows.length
      element.dataset.mode = mode
      element.dataset.version = mapVersion
      const empty = document.getElementById('map-empty')
      empty.style.display = rows.length ? 'none' : 'block'
      empty.textContent = 'No hay ubicaciones utilizables en esta selección.'
      redraw()
      const legend = document.querySelector('.map-legend')
      legend.innerHTML = mode === 'concentration'
        ? '<span style="color:#b4a2fb">■</span> Celdas de 5° × 5° · Más intensidad, más registros <span class="legend-note">Escala de color logarítmica. No representa densidad por km².</span>'
        : '<span class="teal">●</span> Hallazgo <span class="amber">●</span> Caída observada <span style="color:#b4a2fb">●</span> Grupo mixto <span class="legend-note">Punto: tamaño por masa · Grupo: número de registros</span>'
    })
    Shiny.addCustomMessageHandler('atlas-charts', async figures => {
      for (const [id, figure] of Object.entries(figures)) {
        const node = document.getElementById(id)
        figure.layout.autosize = true
        delete figure.layout.width
        delete figure.layout.height
        figure.layout.font = { ...figure.layout.font, family: 'Atlas, Segoe UI, sans-serif', size: 11 }
        if (id === 'boxes-chart') {
          const ticks = [.001, .01, .1, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000]
          figure.layout.yaxis.tickmode = 'array'
          figure.layout.yaxis.tickvals = ticks
          figure.layout.yaxis.ticktext = ticks.map(value => new Intl.NumberFormat('es-CR', { maximumFractionDigits: 3 }).format(value))
        }
        if (window.innerWidth < 600) {
          figure.layout.margin = { ...figure.layout.margin, l: id === 'classes-chart' ? 74 : 58, r: 18, t: 40 }
          figure.layout.font.size = 10
        }
        figure.layout.transition = { duration: (reducedMotion || document.body.classList.contains('motion-paused')) ? 0 : 250 }
        await Plotly.react(node, figure.data, figure.layout, {
          responsive: true, displaylogo: false, locale: 'es', displayModeBar: true,
          scrollZoom: false, modeBarButtonsToRemove: ['select2d', 'lasso2d', 'sendDataToCloud', 'sendChartToCloud'],
          toImageButtonOptions: { format: 'png', filename: `atlas-${id}`, height: 800, width: 1400, scale: 1.5 },
        })
        node.dataset.ready = 'true'
      }
    })
    $(document).on('shiny:sessioninitialized', () => Shiny.setInputValue('client_ready', Date.now(), { priority: 'event' }))
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init)
  else init()
})()
