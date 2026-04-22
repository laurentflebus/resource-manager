import { useState } from "react"
import Login from "./components/Login"
import CalendarView from "./components/CalendarView"
import AdminDashboard from "./components/AdminDashboard"


function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("token")
  )

  const role = localStorage.getItem("role")

  return (
    <div>
      {!loggedIn ? (
        <Login onLogin={() => setLoggedIn(true)} />
      ) : (
        <>
          {role === "admin" && <AdminDashboard />}
          <CalendarView />
        </>
      )}
    </div>
  )
}

export default App