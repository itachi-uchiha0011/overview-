import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../../lib/api'
import { motion } from 'framer-motion'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('accessToken', data.accessToken)
      navigate('/')
    } catch (err: any) {
      setError(err?.response?.data?.msg || 'Login failed')
    }
  }

  return (
    <div className="min-h-[70vh] grid place-items-center px-4">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-sm bg-white dark:bg-zinc-900 rounded-2xl shadow-soft p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blush-400 to-blush-600 cursor-bounce" />
          <div>
            <h1 className="text-xl font-semibold">Hey, welcome back 🌸</h1>
            <p className="text-sm text-zinc-500">We missed your sparkle.</p>
          </div>
        </div>
        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label className="block text-sm mb-1">Email</label>
            <input className="w-full rounded-lg border-zinc-200 dark:border-zinc-800 bg-transparent" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm mb-1">Password</label>
            <input className="w-full rounded-lg border-zinc-200 dark:border-zinc-800 bg-transparent" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
          </div>
          {error && <div className="text-sm text-red-500">{error}</div>}
          <button type="submit" className="w-full rounded-lg bg-gradient-to-tr from-blush-400 to-blush-600 text-white py-2">Login</button>
        </form>
        <p className="text-xs text-zinc-500 mt-3">No account? <Link to="/signup" className="text-blush-500">Create one</Link></p>
      </motion.div>
    </div>
  )
}