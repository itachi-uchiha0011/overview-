import { Outlet, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { MoonIcon, SunIcon } from '@radix-ui/react-icons'

export function AppLayout() {
  const [dark, setDark] = useState<boolean>(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  return (
    <div className="min-h-full flex flex-col bg-white dark:bg-zinc-950">
      <header className="sticky top-0 z-30 backdrop-blur bg-white/70 dark:bg-zinc-950/70 border-b border-zinc-200/60 dark:border-zinc-800/60">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-blush-400 to-blush-600 shadow-soft cursor-bounce" />
            <span className="font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">Overview</span>
          </Link>
          <nav className="flex items-center gap-4">
            <Link to="/" className="text-sm text-zinc-600 dark:text-zinc-300 hover:text-blush-500">Dashboard</Link>
            <Link to="/login" className="text-sm text-zinc-600 dark:text-zinc-300 hover:text-blush-500">Login</Link>
            <Link to="/signup" className="text-sm text-zinc-600 dark:text-zinc-300 hover:text-blush-500">Signup</Link>
            <button aria-label="Toggle dark mode" onClick={() => setDark(v => !v)} className="rounded-lg p-2 hover:bg-zinc-100 dark:hover:bg-zinc-900">
              {dark ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="py-6 text-center text-xs text-zinc-500">Made with love and cursors ✨</footer>
    </div>
  )
}