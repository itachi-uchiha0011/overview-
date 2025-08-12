import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { BlockNoteViewRaw as BlockNoteView, useCreateBlockNote } from '@blocknote/react'
import '@blocknote/react/style.css'

interface Habit { id: number; title: string; logs: { completedOn: string }[] }

export function Dashboard() {
  const [name, setName] = useState<string>('')
  const [habits, setHabits] = useState<Habit[]>([])
  const editor = useCreateBlockNote()

  useEffect(() => {
    api.get('/auth/me').then(res => setName(res.data.user.name)).catch(()=>{})
    api.get('/habits').then(res => setHabits(res.data.habits || [])).catch(()=>{})
  }, [])

  return (
    <div className="mx-auto max-w-6xl p-4 sm:p-6">
      <div className="mb-6 rounded-2xl bg-gradient-to-tr from-blush-50 to-white dark:from-zinc-900 dark:to-zinc-950 border border-zinc-200/60 dark:border-zinc-800/60 p-6">
        <h2 className="text-2xl font-semibold">Hey {name || 'friend'} 🌸</h2>
        <p className="text-zinc-600 dark:text-zinc-400">Here’s your cozy overview.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 rounded-2xl border border-zinc-200/60 dark:border-zinc-800/60 p-4">
          <h3 className="font-semibold mb-3">Habits</h3>
          <ul className="space-y-2">
            {habits.map(h => (
              <li key={h.id} className="flex items-center justify-between">
                <span>{h.title}</span>
                <span className="text-xs text-zinc-500">{h.logs?.length || 0} done</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="lg:col-span-2 rounded-2xl border border-zinc-200/60 dark:border-zinc-800/60 p-4">
          <h3 className="font-semibold mb-3">Journal</h3>
          <BlockNoteView editor={editor} />
        </section>
      </div>
    </div>
  )
}