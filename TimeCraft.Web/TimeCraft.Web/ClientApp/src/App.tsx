import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import TimeCraftApp from './TimeCraftApp'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/generate" replace />} />
        <Route path="/generate" element={<TimeCraftApp defaultView="main" />} />
        <Route path="/datasets" element={<TimeCraftApp defaultView="published" />} />
        <Route path="/datasets/:id" element={<TimeCraftApp defaultView="published" />} />
        <Route path="*" element={<Navigate to="/generate" replace />} />
      </Routes>
    </Router>
  )
}

export default App
