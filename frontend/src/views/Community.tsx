import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { getSocket } from '../lib/socket'

interface Channel { id: number; name: string }
interface Message { id: number; content: string; userId: number; createdAt: string }

export function Community() {
  const { communityId, channelId } = useParams()
  const [channels, setChannels] = useState<Channel[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!communityId) return
    api.get(`/communities/${communityId}/channels`).then(res => setChannels(res.data.channels || []))
  }, [communityId])

  useEffect(() => {
    if (!channelId) return
    api.get(`/communities/channels/${channelId}/messages`).then(res => setMessages(res.data.messages || []))
    const s = getSocket()
    s.connect()
    s.emit('join', { channelId: Number(channelId) })
    s.on('message', (m: any) => {
      if (m.channelId === Number(channelId)) setMessages(prev => [...prev, m as Message])
    })
    s.on('typing', () => {})
    return () => {
      s.emit('leave', { channelId: Number(channelId) })
      s.off('message')
    }
  }, [channelId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length])

  function send() {
    const content = input.trim()
    if (!content || !channelId) return
    getSocket().emit('message', { channelId: Number(channelId), content })
    setInput('')
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 p-4">
      <aside className="lg:col-span-3 rounded-2xl border border-zinc-200/60 dark:border-zinc-800/60 p-3 h-[70vh] overflow-y-auto">
        <h3 className="text-sm uppercase tracking-wide text-zinc-500 mb-2">Channels</h3>
        <ul className="space-y-1">
          {channels.map(c => (
            <li key={c.id} className={`px-3 py-2 rounded-lg ${String(c.id)===channelId? 'bg-blush-50 dark:bg-zinc-900 text-blush-600 dark:text-blush-400' : 'hover:bg-zinc-50 dark:hover:bg-zinc-900'}`}>{c.name}</li>
          ))}
        </ul>
      </aside>
      <section className="lg:col-span-9 rounded-2xl border border-zinc-200/60 dark:border-zinc-800/60 flex flex-col h-[70vh]">
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map(m => (
            <div key={m.id} className="text-sm">
              <span className="text-zinc-500 mr-2">{new Date(m.createdAt).toLocaleTimeString()}</span>
              <span>{m.content}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="border-t border-zinc-200/60 dark:border-zinc-800/60 p-3 flex gap-2">
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{ if(e.key==='Enter') send() }} placeholder="Write something nice ✨" className="flex-1 rounded-lg border-zinc-200 dark:border-zinc-800 bg-transparent" />
          <button onClick={send} className="rounded-lg px-3 bg-gradient-to-tr from-blush-400 to-blush-600 text-white">Send</button>
        </div>
      </section>
    </div>
  )
}