import React, { createContext, useContext, useState } from "react"

type Progress = {
  completedLevel: number
  unlockedLevel: number
}

type SessionState = {
  token: string | null
  setToken: (t: string | null) => void
  progress: Progress | null
  setProgress: (p: Progress | null) => void
}

const SessionContext = createContext<SessionState | null>(null)

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"))
  const [progress, setProgress] = useState<Progress | null>(null)

  const setTokenAndPersist = (t: string | null) => {
    setToken(t)
    if (t) localStorage.setItem("token", t)
    else localStorage.removeItem("token")
  }

  return (
    <SessionContext.Provider
      value={{ token, setToken: setTokenAndPersist, progress, setProgress }}
    >
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error("useSession must be used inside SessionProvider")
  return ctx
}
