// src/services/api.ts
import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

// Axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
})

// Request interceptor (adds token if present)
apiClient.interceptors.request.use(
  (config) => {
    const token =
      typeof window !== "undefined" ? localStorage.getItem("access_token") : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor (handles 401)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token")
    }
    return Promise.reject(error)
  }
)

// ----------------------------
// Types
// ----------------------------
interface RegisterData {
  email: string
  password: string
  full_name: string
}

interface LoginData {
  email: string
  password: string
}

interface UpdateUserData {
  full_name?: string
}

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

interface HealthResponse {
  status: string
  timestamp: string
}

// ----------------------------
// API Service Class
// ----------------------------
class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  // Health
  async health(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>("/health")
    return response.data
  }

  // Auth
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/register", data)
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/login", data)
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async me(): Promise<User> {
    const response = await apiClient.get<User>("/auth/me")
    return response.data
  }

  async verifyEmail(token: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `token=${token}`,
    })
    if (!response.ok) throw new Error("Email verification failed")
    return response.json()
  }

  async refreshToken(): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/refresh")
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async logout(): Promise<void> {
    await apiClient.post("/auth/logout")
    localStorage.removeItem("access_token")
  }

  // Users
  async listUsers(skip: number = 0, limit: number = 10): Promise<User[]> {
    const response = await apiClient.get<User[]>(`/users?skip=${skip}&limit=${limit}`)
    return response.data
  }

  async countUsers(): Promise<{ count: number }> {
    const response = await apiClient.get<{ count: number }>("/users/count")
    return response.data
  }

  async getUserById(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${userId}`)
    return response.data
  }

  async updateUser(userId: string, data: UpdateUserData): Promise<User> {
    const response = await apiClient.put<User>(`/users/${userId}`, data)
    return response.data
  }

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/users/${userId}`)
  }

  // Ingest
  async ingestData(): Promise<any> {
    const response = await apiClient.get("/ingest")
    return response.data
  }
}

// ----------------------------
// Streaming chat (SSE)
// ----------------------------
export async function sendMessageStream(
  query: string,
  onMessage: (token: string) => void
): Promise<void> {
  const url = `${API_BASE_URL}/api/chat/stream?query=${encodeURIComponent(query)}`

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "text/event-stream",
    },
  })

  if (!response.body) {
    throw new Error("No response body received from server")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder("utf-8")

  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split("\n")

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.replace("data: ", "").trim()
          if (data === "[DONE]") {
            return
          }
          onMessage(data)
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

// ----------------------------
// WebSocket chat
// ----------------------------
export class WebSocketChat {
  private ws: WebSocket | null = null
  private onMessage: ((message: string) => void) | null = null
  private onError: ((error: string) => void) | null = null
  private onConnect: (() => void) | null = null
  private onDisconnect: (() => void) | null = null

  connect(
    onMessage: (message: string) => void,
    onError: (error: string) => void,
    onConnect?: () => void,
    onDisconnect?: () => void
  ): void {
    this.onMessage = onMessage
    this.onError = onError
    this.onConnect = onConnect
    this.onDisconnect = onDisconnect

    try {
      const wsUrl = API_BASE_URL.replace("http://", "ws://").replace(
        "https://",
        "wss://"
      )
      this.ws = new WebSocket(`${wsUrl}/api/ws/chat`)

      this.ws.onopen = () => {
        console.log("WebSocket connected")
        this.onConnect?.()
      }

      this.ws.onmessage = (event) => {
        this.onMessage?.(event.data)
      }

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        this.onError?.("WebSocket connection error")
      }

      this.ws.onclose = () => {
        console.log("WebSocket disconnected")
        this.onDisconnect?.()
      }
    } catch (error: any) {
      console.error("Error creating WebSocket:", error)
      this.onError?.(error.message || "Failed to create WebSocket connection")
    }
  }

  sendMessage(message: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message)
    } else {
      console.error("WebSocket is not connected")
      this.onError?.("WebSocket is not connected")
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// ----------------------------
// Utility
// ----------------------------
const generateSessionId = (): string => {
  return "session_" + Math.random().toString(36).substr(2, 9) + "_" + Date.now()
}

// ----------------------------
// Exports
// ----------------------------
export const api = new ApiService()
export { apiClient, generateSessionId }
export type { User, RegisterData, LoginData, UpdateUserData, AuthResponse, HealthResponse }
