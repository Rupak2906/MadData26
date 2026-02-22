import { Routes, Route } from "react-router-dom"
import Home from "./pages/Home"
import Intake from "./pages/Intake"
import Analyzing from "./pages/Analyzing"
import Dashboard from "./pages/Dashboard"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/intake" element={<Intake />} />
      <Route path="/analyzing" element={<Analyzing />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  )
}

export default App