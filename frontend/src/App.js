import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Layout from "./components/Layout"
import CalendarView from "./components/CalendarView"
import AdminDashboard from "./components/AdminDashboard"
import Login from "./components/Login"
import { useState } from "react"

function App() {

  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("token")
  )

  const role = localStorage.getItem("role")

  return (
    <BrowserRouter>

      {!loggedIn ? (
        <Login onLogin={() => setLoggedIn(true)} />
      ) : (
        <Routes>
          <Route
            path="/"
            element={
              <Layout>
                <CalendarView />
              </Layout>
            }
          />
          <Route
            path="/admin"
            element={
              role === "admin"
                ? (
                  <Layout>
                    <AdminDashboard />
                  </Layout>
                )
                : <Navigate to="/" />
            }
          />
          <Route path="*" element={<Navigate to="/" />} />

        </Routes>
      )}

    </BrowserRouter>
  )
}

export default App