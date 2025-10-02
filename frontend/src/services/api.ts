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
    console.log("Calling health endpoint")
    const response = await apiClient.get<HealthResponse>("/health")
    return response.data
  }

  // Auth
  async register(data: RegisterData): Promise<AuthResponse> {
    console.log("Calling register endpoint with data:", data)
    const response = await apiClient.post<AuthResponse>("/auth/register", data)
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async login(data: LoginData): Promise<AuthResponse> {
    console.log("Calling login endpoint with data:", data)
    const response = await apiClient.post<AuthResponse>("/auth/login", data)
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async me(): Promise<User> {
    console.log("Calling me endpoint")
    const response = await apiClient.get<User>("/auth/me")
    return response.data
  }

  async verifyEmail(token: string): Promise<any> {
    console.log("Calling verifyEmail endpoint with token:", token)
    const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `token=${token}`,
    })
    if (!response.ok) throw new Error("Email verification failed")
    return response.json()
  }

  async refreshToken(): Promise<AuthResponse> {
    console.log("Calling refreshToken endpoint")
    const response = await apiClient.post<AuthResponse>("/auth/refresh")
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token)
    }
    return response.data
  }

  async logout(): Promise<void> {
    console.log("Calling logout endpoint")
    await apiClient.post("/auth/logout")
    localStorage.removeItem("access_token")
  }

  // Users
  async listUsers(skip: number = 0, limit: number = 10): Promise<User[]> {
    console.log("Calling listUsers endpoint with skip:", skip, "limit:", limit)
    const response = await apiClient.get<User[]>(`/users?skip=${skip}&limit=${limit}`)
    return response.data
  }

  async countUsers(): Promise<{ count: number }> {
    console.log("Calling countUsers endpoint")
    const response = await apiClient.get<{ count: number }>("/users/count")
    return response.data
  }

  async getUserById(userId: string): Promise<User> {
    console.log("Calling getUserById endpoint with userId:", userId)
    const response = await apiClient.get<User>(`/users/${userId}`)
    return response.data
  }

  async updateUser(userId: string, data: UpdateUserData): Promise<User> {
    console.log("Calling updateUser endpoint with userId:", userId, "data:", data)
    const response = await apiClient.put<User>(`/users/${userId}`, data)
    return response.data
  }

  async deleteUser(userId: string): Promise<void> {
    console.log("Calling deleteUser endpoint with userId:", userId)
    await apiClient.delete(`/users/${userId}`)
  }

  // Ingest
  async ingestData(): Promise<any> {
    console.log("Calling ingestData endpoint")
    const response = await apiClient.get("/ingest")
    return response.data
  }
}

// ----------------------------
// Streaming chat (SSE) - Updated to support images
// ----------------------------
export async function sendMessageStream(
  query: string,
  onMessage: (token: string) => void,
  imageFile?: File | null
): Promise<void> {
  console.log("Calling sendMessageStream with query:", query, "imageFile:", !!imageFile)

  let url: string
  let requestOptions: RequestInit

  console.log('sendMessageStream called with:')
  console.log('- query:', query)
  console.log('- imageFile:', imageFile)
  console.log('- imageFile exists:', !!imageFile)

  if (imageFile) {
    console.log('Using POST with image')
    // Send as multipart/form-data if image is present
    const formData = new FormData()
    formData.append("query", query)
    formData.append("image", imageFile)

    url = `${API_BASE_URL}/api/chat/stream`
    requestOptions = {
      method: "POST",
      headers: {
        Accept: "text/event-stream",
      },
      body: formData,
    }
  } else {
    console.log('Using GET without image')
    // Send as GET request with query parameter if no image
    url = `${API_BASE_URL}/api/chat/stream?query=${encodeURIComponent(query)}`
    requestOptions = {
      method: "GET",
      headers: {
        Accept: "text/event-stream",
      },
    }
  }

  console.log('Request URL:', url)
  console.log('Request method:', requestOptions.method)

  const response = await fetch(url, requestOptions)

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
    console.log("Calling WebSocketChat connect")
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
    console.log("Calling WebSocketChat sendMessage with message:", message)
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message)
    } else {
      console.error("WebSocket is not connected")
      this.onError?.("WebSocket is not connected")
    }
  }

  disconnect(): void {
    console.log("Calling WebSocketChat disconnect")
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    console.log("Calling WebSocketChat isConnected")
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
