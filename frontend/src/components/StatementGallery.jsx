import React from 'react'

// Read-only anonymous gallery of statement cards (used inside voting & reveal).
export default function StatementGallery({ statements }) {
  return (
    <div className="statement-grid">
      {statements.map((s) => (
        <div key={s.index} className={`statement-card glass ${s.is_yours ? 'is-yours' : ''}`}>
          <span className="statement-letter">{s.letter}</span>
          <p className="statement-text">{s.text}</p>
          {s.is_yours && <span className="yours-badge">your card</span>}
        </div>
      ))}
    </div>
  )
}
