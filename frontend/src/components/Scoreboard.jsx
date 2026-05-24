import React from 'react'

export default function Scoreboard({ scores, roundScores, you }) {
  return (
    <div className="card glass">
      <h3 className="section-title">Scoreboard</h3>
      <ul className="scoreboard">
        {scores.map((s, i) => {
          const delta = roundScores ? roundScores[s.id] : null
          return (
            <li key={s.id} className={`score-row ${s.id === you ? 'is-you' : ''}`}>
              <span className="rank">{i + 1}</span>
              <span className="score-name">{s.name}</span>
              {delta != null && delta !== 0 && (
                <span className="score-delta">+{delta}</span>
              )}
              <span className="score-total">{s.score}</span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
