import { useState } from "react"
import Login from "./components/Login"
import CalendarView from "./components/CalendarView"


function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("token")
  )

  return (
    <div>
      {!loggedIn ? (
        <Login onLogin={() => setLoggedIn(true)} />
      ) : (
        <CalendarView />
      )}
    </div>
  )
}

export default App