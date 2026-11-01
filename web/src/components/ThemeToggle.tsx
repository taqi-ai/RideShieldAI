import { Moon, Sun } from '@phosphor-icons/react'
import { useTheme } from '../hooks/useTheme'

export function ThemeToggle() {
  const { theme, toggle } = useTheme()
  const toDay = theme === 'dark'
  return (
    <button className="icon-btn" onClick={toggle} aria-label={toDay ? 'Switch to day mode' : 'Switch to night mode'} title={toDay ? 'Day mode' : 'Night mode'}>
      {toDay ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
