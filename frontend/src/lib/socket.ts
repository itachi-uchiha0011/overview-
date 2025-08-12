import { io, Socket } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

let socket: Socket | null = null

export function getSocket(): Socket {
  if (socket) return socket
  const token = localStorage.getItem('accessToken')
  socket = io(SOCKET_URL, {
    transports: ['websocket'],
    autoConnect: !!token,
    query: token ? { token } : undefined,
  })
  return socket
}