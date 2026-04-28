import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Layout from "./components/Layout"
import CalendarView from "./components/CalendarView"
import AdminDashboard from "./components/AdminDashboard"
import Login from "./components/Login"
import { useAuth } from "./context/AuthContext"

function App() {
    const { isLoggedIn, role } = useAuth()

    return (
        <BrowserRouter>
            {!isLoggedIn ? (
                <Login />
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