import "./Intermediate.css"
import { useEffect, useRef, useState } from "react"

const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"

const API_BASE = "http://localhost:5001"

type SignPrompt = {
  label: string
  description: string
}

type CheckResult = {
  success: boolean
  match: boolean
  target: string
  prediction: string
  confidence: number
  message?: string
}

export default function Intermediate() {
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const landmarkerRef = useRef<any>(null)
  const animationRef = useRef<number | null>(null)
  const lastLandmarksRef = useRef<any[] | null>(null)
  const lastVideoTimeRef = useRef<number>(-1)

  const [cameraReady, setCameraReady] = useState(false)
  const [modelReady, setModelReady] = useState(false)
  const [status, setStatus] = useState("Loading hand tracking model...")
  const [error, setError] = useState("")
  const [checking, setChecking] = useState(false)
  const [result, setResult] = useState<CheckResult | null>(null)
  const [promptIndex, setPromptIndex] = useState(0)

  const supportedLabels = new Set(["A", "B", "C", "D", "E"])
  const promptDescriptions: Record<string, string> = {
    A: "Make a fist with your thumb resting on the side.",
    B: "Hold a flat open palm with fingers together.",
    C: "Curve your fingers to form a C shape.",
    D: "Point your index finger up, with other fingers folded in.",
    E: "Curl all fingers into your palm with the thumb tucked.",
  }
  const prompts: SignPrompt[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((label) => ({
    label,
    description:
      promptDescriptions[label] || `Practice the ${label} fingerspelling handshape.`,
  }))

  useEffect(() => {
    let active = true

    const setup = async () => {
      try {
        setStatus("Loading AI hand tracker...")
        const vision = await import(
          /* @vite-ignore */ "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14"
        )
        const { FilesetResolver, HandLandmarker } = vision

        const fileset = await FilesetResolver.forVisionTasks(WASM_URL)
        if (!active) return

        landmarkerRef.current = await HandLandmarker.createFromOptions(fileset, {
          baseOptions: { modelAssetPath: MODEL_URL },
          runningMode: "VIDEO",
          numHands: 1,
        })

        setModelReady(true)
        setStatus("Model ready. Allow camera access to start tracking.")

        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (!active) return

        const video = videoRef.current
        if (!video) return

        video.srcObject = stream
        await video.play()
        setCameraReady(true)
        setStatus("Tracking enabled. Show your hand to the camera.")

        const canvas = canvasRef.current
        if (canvas) {
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
        }

        const detect = () => {
          if (!video || !landmarkerRef.current) return
          const nowInMs = performance.now()
          if (lastVideoTimeRef.current !== video.currentTime) {
            lastVideoTimeRef.current = video.currentTime
            const results = landmarkerRef.current.detectForVideo(video, nowInMs)
            const landmarks = results?.landmarks?.[0] ?? null
            lastLandmarksRef.current = landmarks
            drawLandmarks(landmarks)
          }
          animationRef.current = requestAnimationFrame(detect)
        }

        detect()
      } catch (err) {
        console.error(err)
        setError("Could not start hand tracking. Check camera permissions.")
        setStatus("Hand tracking unavailable.")
      }
    }

    setup()

    return () => {
      active = false
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      const stream = videoRef.current?.srcObject as MediaStream | null
      stream?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  const drawLandmarks = (landmarks: any[] | null) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (!landmarks) return

    ctx.fillStyle = "#3b82f6"
    landmarks.forEach((point) => {
      const x = point.x * canvas.width
      const y = point.y * canvas.height
      ctx.beginPath()
      ctx.arc(x, y, 5, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  const handleCheck = async () => {
    setError("")
    setResult(null)

    const landmarks = lastLandmarksRef.current
    if (!landmarks) {
      setError("No hand detected yet. Try showing your hand to the camera.")
      return
    }

    setChecking(true)
    try {
      const res = await fetch(`${API_BASE}/asl/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: prompts[promptIndex].label,
          landmarks,
        }),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data?.message || "Backend returned an error.")
        return
      }
      setResult(data)
    } catch (err) {
      console.error(err)
      setError("Unable to reach the backend server. Is Flask running?")
    } finally {
      setChecking(false)
    }
  }

  const handleNext = () => {
    setResult(null)
    setError("")
    setPromptIndex((prev) => (prev + 1) % prompts.length)
  }

  return (
    <div className="intermediate-page">
      <div className="intermediate-card">
        <header className="intermediate-header">
          <p className="intermediate-kicker">Intermediate · AI Practice</p>
          <h1>Live Hand Tracking Practice</h1>
          <p className="intermediate-subtitle">
            The camera uses Google MediaPipe Hand Landmarker (loaded online) to
            detect your hand and send landmarks to the Flask backend for
            scoring.
          </p>
          <p className="intermediate-subtitle">
            Current recognition supports: A, B, C, D, E. Other letters will return
            Unknown until more training data is added.
          </p>
        </header>

        <section className="intermediate-prompt">
          <div>
            <h2>Current sign: {prompts[promptIndex].label}</h2>
            <p>{prompts[promptIndex].description}</p>
          </div>
          <div className="prompt-actions">
            <button className="primary-btn" onClick={handleCheck} disabled={checking}>
              {checking ? "Checking..." : "Check my sign"}
            </button>
            <button className="secondary-btn" onClick={handleNext}>
              Next sign
            </button>
          </div>
        </section>

        <section className="tracking-area">
          <div className="video-wrapper">
            <video ref={videoRef} className="tracking-video" muted playsInline />
            <canvas ref={canvasRef} className="tracking-canvas" />
          </div>
          <aside className="tracking-status">
            <p>
              <strong>Status:</strong> {status}
            </p>
            <p>
              <strong>Model:</strong> {modelReady ? "Ready" : "Loading"}
            </p>
            <p>
              <strong>Camera:</strong> {cameraReady ? "Active" : "Waiting"}
            </p>
            {error && <p className="error-text">{error}</p>}
            {result && (
              <div
                className={`result-card ${
                  result.match && result.prediction !== "Unknown" ? "success" : "fail"
                }`}
              >
                <p>
                  <strong>Target:</strong> {result.target}
                </p>
                <p>
                  <strong>Prediction:</strong> {result.prediction}
                </p>
                <p>
                  <strong>Confidence:</strong> {(result.confidence * 100).toFixed(0)}%
                </p>
                <p className="result-message">
                  {!supportedLabels.has(result.target)
                    ? "Recognition currently supports A–E only. More letters are coming soon."
                    : result.prediction === "Unknown"
                    ? "We couldn't recognize that sign yet."
                    : result.match
                    ? "Nice work!"
                    : "Keep practicing and try again."}
                </p>
              </div>
            )}
          </aside>
        </section>
      </div>
    </div>
  )
}
