import Navbar from "./Navbar"
import Sidebar from "./Sidebar"

export default function Layout({ children }) {
    return (
        <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>

            <Navbar />

            <div style={{ display: "flex", flex: 1 }}>

                <Sidebar />

                <div style={{ flex: 1, padding: 20 }}>
                    {children}
                </div>

            </div>
        </div>
    )
}