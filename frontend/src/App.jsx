import { useEffect, useRef, useState } from 'react'
import './App.css'

const formatNumber = (value) => Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: 1 })
const apiBase = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')
const apiUrl = (path) => `${apiBase}/api${path}`

function App() {
  const [summary, setSummary] = useState(null)
  const [inventory, setInventory] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeNav, setActiveNav] = useState('Dashboard')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [uploadError, setUploadError] = useState('')
  const fileInputRef = useRef(null)

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [summaryRes, inventoryRes, recRes] = await Promise.all([
          fetch(apiUrl('/dashboard/summary')),
          fetch(apiUrl('/inventory')),
          fetch(apiUrl('/recommendations')),
        ])

        const summaryData = await summaryRes.json()
        const inventoryData = await inventoryRes.json()
        const recData = await recRes.json()

        setSummary(summaryData.data)
        setInventory(inventoryData.data)
        setRecommendations(recData.data)
      } catch (error) {
        console.error('Dashboard load failed', error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [])

  const handleNavClick = (label) => {
    setActiveNav(label)
  }

  const handleLogin = () => {
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
  }

  const handleBrowseFiles = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadError('Please upload a CSV file.')
      setUploadMessage('')
      event.target.value = ''
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(apiUrl('/upload/inventory'), {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()

      if (!response.ok || result.success === false) {
        setUploadError(result.message || 'CSV validation failed.')
        setUploadMessage('')
        event.target.value = ''
        return
      }

      setUploadError('')
      setUploadMessage(`Validated ${result.data.row_count} rows in ${file.name}. Ready for import.`)
    } catch (error) {
      console.error('CSV file processing failed', error)
      setUploadError('Unable to read the selected CSV file.')
      setUploadMessage('')
    } finally {
      event.target.value = ''
    }
  }

  const handleExportCsv = () => {
    if (!recommendations.length) return

    const csvHeader = ['Bar', 'Brand', 'Current Stock', 'Par Level', 'Reorder Point', 'Suggested Order', 'Risk Level']
    const csvRows = recommendations.map((row) => [
      row.bar,
      row.brand,
      row.current_stock,
      row.par_level,
      row.reorder_point,
      row.suggested_order,
      row.risk_level,
    ])

    const csvContent = [csvHeader, ...csvRows]
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'inventory_recommendations.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return <div className="loading">Loading inventory dashboard…</div>
  }

  const kpis = [
    { label: 'Total Inventory', value: formatNumber(summary?.total_inventory), tone: 'primary' },
    { label: 'Items at Risk', value: summary?.items_at_risk ?? 0, tone: 'warning' },
    { label: 'Predicted Demand', value: formatNumber(summary?.predicted_demand), tone: 'success' },
    { label: 'Recommended Orders', value: formatNumber(summary?.recommended_orders), tone: 'accent' },
  ]

  const renderView = () => {
    if (activeNav === 'Inventory') {
      return (
        <section className="panel table-panel">
          <div className="panel-header">
            <h3>Inventory Overview</h3>
            <button type="button" className="ghost-button" onClick={handleExportCsv}>Export CSV</button>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Bar</th>
                  <th>Brand</th>
                  <th>Current Stock</th>
                  <th>Average Daily Consumption</th>
                  <th>Lead Time</th>
                  <th>Safety Stock</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((row) => (
                  <tr key={`${row.bar}-${row.brand}`}>
                    <td>{row.bar}</td>
                    <td>{row.brand}</td>
                    <td>{row.current_stock}</td>
                    <td>{row.average_daily_consumption}</td>
                    <td>{row.lead_time_days}</td>
                    <td>{Number(row.safety_stock).toFixed(1)}</td>
                    <td><span className={`pill ${row.stock_status === 'Healthy' ? 'healthy' : 'warning'}`}>{row.stock_status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )
    }

    if (activeNav === 'Forecasting') {
      return (
        <section className="view-grid">
          <div className="panel">
            <div className="panel-header">
              <h3>Forecast Models</h3>
              <span>Validated</span>
            </div>
            <div className="stats-grid">
              <div className="mini-stat"><strong>Baseline</strong><span>MAE 4.2</span></div>
              <div className="mini-stat"><strong>Holt-Winters</strong><span>MAE 3.8</span></div>
              <div className="mini-stat"><strong>Random Forest</strong><span>MAE 3.5</span></div>
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">
              <h3>Weekday Demand</h3>
              <span>Weekend effect</span>
            </div>
            <div className="chart-bars compact">
              {[26, 34, 38, 62, 82, 95, 88].map((value, index) => (
                <div key={index} className="bar-wrap"><div className="bar" style={{ height: `${value}%` }} /></div>
              ))}
            </div>
          </div>
        </section>
      )
    }

    if (activeNav === 'Recommendations') {
      return (
        <section className="panel table-panel">
          <div className="panel-header">
            <h3>Recommendation Engine</h3>
            <button type="button" className="ghost-button" onClick={handleExportCsv}>Export CSV</button>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Bar</th>
                  <th>Brand</th>
                  <th>Current Stock</th>
                  <th>Par Level</th>
                  <th>Reorder Point</th>
                  <th>Suggested Order</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {recommendations.map((row) => (
                  <tr key={`${row.bar}-${row.brand}`}>
                    <td>{row.bar}</td>
                    <td>{row.brand}</td>
                    <td>{row.current_stock}</td>
                    <td>{Number(row.par_level).toFixed(1)}</td>
                    <td>{Number(row.reorder_point).toFixed(1)}</td>
                    <td>{Number(row.suggested_order).toFixed(1)}</td>
                    <td><span className={`pill ${row.risk_level === 'Healthy' ? 'healthy' : 'warning'}`}>{row.risk_level}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )
    }

    if (activeNav === 'Simulation') {
      return (
        <section className="view-grid">
          <div className="panel">
            <div className="panel-header">
              <h3>Simulation Summary</h3>
              <span>Policy impact</span>
            </div>
            <div className="stats-grid">
              <div className="mini-stat"><strong>Stockout Days</strong><span>4.8</span></div>
              <div className="mini-stat"><strong>Service Level</strong><span>96.4%</span></div>
              <div className="mini-stat"><strong>Avg. Inventory</strong><span>42.2</span></div>
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">
              <h3>Inventory Trajectory</h3>
              <span>Projected</span>
            </div>
            <div className="chart-bars compact">
              {[48, 58, 54, 70, 68, 82, 78, 92, 88, 74].map((value, index) => (
                <div key={index} className="bar-wrap"><div className="bar" style={{ height: `${value}%` }} /></div>
              ))}
            </div>
          </div>
        </section>
      )
    }

    if (activeNav === 'Analytics') {
      return (
        <section className="view-grid">
          <div className="panel">
            <div className="panel-header">
              <h3>ABC Analysis</h3>
              <span>Velocity mix</span>
            </div>
            <div className="stats-grid">
              <div className="mini-stat"><strong>A Items</strong><span>32%</span></div>
              <div className="mini-stat"><strong>B Items</strong><span>41%</span></div>
              <div className="mini-stat"><strong>C Items</strong><span>27%</span></div>
            </div>
          </div>
          <div className="panel">
            <div className="panel-header">
              <h3>Stockout Distribution</h3>
              <span>By brand</span>
            </div>
            <ul className="status-list">
              <li><span className="status-dot healthy" /> Gin<span>18%</span></li>
              <li><span className="status-dot warning" /> Vodka<span>26%</span></li>
              <li><span className="status-dot critical" /> Whiskey<span>31%</span></li>
            </ul>
          </div>
        </section>
      )
    }

    if (activeNav === 'Data Upload') {
      return (
        <section className="panel upload-panel">
          <div className="panel-header">
            <h3>Data Upload</h3>
            <span>CSV ingestion</span>
          </div>
          <div className="upload-box">
            <input ref={fileInputRef} type="file" accept=".csv" hidden onChange={handleFileChange} />
            <div className="upload-icon">⬆</div>
            <h4>Drag and drop your CSV file</h4>
            <p>Required columns: Date Time Served, Bar Name, Brand Name, Opening Balance, Purchase, Consumed, Closing Balance</p>
            <button type="button" className="primary-button" onClick={handleBrowseFiles}>Browse files</button>
            {uploadError && <p className="upload-status error">{uploadError}</p>}
            {uploadMessage && <p className="upload-status success">{uploadMessage}</p>}
          </div>
        </section>
      )
    }

    return (
      <>
        <section className="kpi-grid">
          {kpis.map((item) => (
            <div key={item.label} className={`kpi-card ${item.tone}`}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </section>

        <section className="content-grid">
          <div className="panel wide">
            <div className="panel-header">
              <h3>Demand Trend</h3>
              <span>Demo Data</span>
            </div>
            <div className="chart-bars" aria-label="Demand trend chart">
              {[42, 62, 58, 71, 88, 96, 84, 72, 66, 90, 100, 76].map((value, index) => (
                <div key={index} className="bar-wrap">
                  <div className="bar" style={{ height: `${value}%` }} />
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h3>Inventory Health</h3>
              <span>Risk View</span>
            </div>
            <ul className="status-list">
              <li><span className="status-dot healthy" /> Healthy<span>68%</span></li>
              <li><span className="status-dot warning" /> Low Stock<span>21%</span></li>
              <li><span className="status-dot critical" /> Critical<span>11%</span></li>
            </ul>
          </div>
        </section>

        <section className="panel table-panel">
          <div className="panel-header">
            <h3>Inventory Recommendations</h3>
            <button type="button" className="ghost-button" onClick={handleExportCsv}>Export CSV</button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Bar</th>
                  <th>Brand</th>
                  <th>Current Stock</th>
                  <th>Par Level</th>
                  <th>Reorder Point</th>
                  <th>Suggested Order</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {recommendations.slice(0, 8).map((row) => (
                  <tr key={`${row.bar}-${row.brand}`}>
                    <td>{row.bar}</td>
                    <td>{row.brand}</td>
                    <td>{row.current_stock}</td>
                    <td>{Number(row.par_level).toFixed(1)}</td>
                    <td>{Number(row.reorder_point).toFixed(1)}</td>
                    <td>{Number(row.suggested_order).toFixed(1)}</td>
                    <td><span className={`pill ${row.risk_level === 'Healthy' ? 'healthy' : 'warning'}`}>{row.risk_level}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">KB</div>
          <div>
            <h2>KristalBar</h2>
            <small>Operations</small>
          </div>
        </div>

        <nav className="nav" aria-label="Primary navigation">
          {['Dashboard', 'Inventory', 'Forecasting', 'Recommendations', 'Simulation', 'Analytics', 'Data Upload'].map((item) => (
            <button
              key={item}
              className={item === activeNav ? 'nav-item active' : 'nav-item'}
              type="button"
              onClick={() => handleNavClick(item)}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Hotel chain overview</p>
            <h1># Bar Inventory Forecasting</h1>
          </div>

          <div className="header-actions">
            <div className="user-badge">
              <span className="avatar">PS</span>
              <div>
                <strong>{isLoggedIn ? 'Pullam Sandeep' : 'Guest User'}</strong>
                <small>{isLoggedIn ? 'Bar Manager' : 'Not signed in'}</small>
              </div>
            </div>

            <div className="auth-actions">
              {!isLoggedIn ? (
                <button type="button" className="secondary-button" onClick={handleLogin}>Login</button>
              ) : (
                <button type="button" className="primary-button" onClick={handleLogout}>Logout</button>
              )}
            </div>
          </div>
        </header>

        {renderView()}
      </main>
    </div>
  )
}

export default App
