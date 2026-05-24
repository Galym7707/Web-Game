import React from 'react'

const ROLE_THEME = {
  curator: { tag: 'role-curator', icon: '🎩' },
  ai_defender: { tag: 'role-ai', icon: '🤖' },
  fake_critic: { tag: 'role-critic', icon: '🎭' },
}

export default function RoleCard({ task }) {
  if (!task) return null
  const theme = ROLE_THEME[task.role] || {}
  return (
    <div className={`role-card glass ${theme.tag}`}>
      <div className="role-head">
        <span className="role-icon">{theme.icon}</span>
        <div>
          <p className="role-label">{task.role_label}</p>
          <h3 className="role-headline">{task.headline}</h3>
        </div>
      </div>
      <p className="role-instructions">{task.instructions}</p>

      {task.curator_notes && (
        <div className="role-hints">
          <p className="hints-title">Your private curator notes</p>
          <ul>{task.curator_notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
        </div>
      )}

      {task.ai_statement && (
        <div className="role-hints">
          <p className="hints-title">The AI statement to disguise</p>
          <blockquote className="ai-quote">{task.ai_statement}</blockquote>
        </div>
      )}

      {task.mood_words && (
        <div className="role-hints">
          <p className="hints-title">Inspiration (optional)</p>
          <div className="chip-row">
            {task.mood_words.map((w, i) => <span key={i} className="hint-chip">{w}</span>)}
          </div>
          <div className="chip-row">
            {task.visual_anchors.map((w, i) => <span key={i} className="hint-chip subtle">{w}</span>)}
          </div>
        </div>
      )}
    </div>
  )
}
