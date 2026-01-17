import { Routes, Route, Navigate } from "react-router-dom"
import Login from "./LoginPage"
import Continue from "./Continue"
import Home from "./Home"
import { useSession } from "./session/SessionContext"
import { ReactNode } from "react"

/* Protect routes that require login */
function RequireAuth({ children }: { children: ReactNode }) {
  const { token } = useSession()
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/continue"
        element={
          <RequireAuth>
            <Continue />
          </RequireAuth>
        }
      />

      <Route
        path="/home"
        element={
          <RequireAuth>
            <Home />
          </RequireAuth>
        }
      />

      {/* fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
