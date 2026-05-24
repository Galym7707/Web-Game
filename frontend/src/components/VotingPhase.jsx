import React, { useState } from 'react'
import { api } from '../api'
import ArtworkStage from './ArtworkStage'

const QUESTIONS = [
  { key: 'real', label: 'Which is the real curator?', hint: 'The true interpretation.' },
  { key: 'ai', label: 'Which one was written by AI?', hint: 'The disguised machine.' },
  { key: 'bluff', label: 'Best bluff?', hint: 'The most convincing fake.' },
]

export default function VotingPhase({ state, session, onVoted }) {
  const [picks, setPicks] = useState({ real: null, ai: null, bluff: null })
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)

  const voted = state.voted
  const statements = state.statements || []

  function pick(qKey, index) {
    setPicks((p) => ({ ...p, [qKey]: index }))
  }

  const ready = picks.real != null && picks.ai != null && picks.bluff != null

  async function handleVote() {
    if (busy || voted || !ready) return
    setBusy(true)
    setErr(null)
    try {
      await api.vote(state.code, session.playerId, picks.real, picks.ai, picks.bluff)
      onVoted()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="screen play">
      <div className="play-grid">
        <div className="play-left">
          <ArtworkStage artwork={state.artwork} round={state.round_number} />
        </div>

        <div className="play-right">
          {voted ? (
            <div className="card glass waiting-card">
              <h3>Vote locked in ✓</h3>
              <p className="waiting-text">
                Waiting for other players… ({state.voted_count}/{state.player_count})
              </p>
              <div className="mini-progress">
                <div className="mini-bar" style={{ width: `${(state.voted_count / state.player_count) * 100}%` }} />
              </div>
            </div>
          ) : (
            <>
              <div className="card glass">
                <h3 className="section-title">The Gallery</h3>
                <div className="vote-statements">
                  {statements.map((s) => (
                    <div key={s.index} className={`vote-card glass ${s.is_yours ? 'is-yours' : ''}`}>
                      <span className="statement-letter">{s.letter}</span>
                      <p className="statement-text">{s.text}</p>
                      {s.is_yours && <span className="yours-badge">your card</span>}
                    </div>
                  ))}
                </div>
              </div>

              <div className="card glass">
                {QUESTIONS.map((q) => (
                  <div key={q.key} className="vote-question">
                    <p className="vote-q-label">{q.label}</p>
                    <p className="vote-q-hint">{q.hint}</p>
                    <div className="letter-row">
                      {statements.map((s) => (
                        <button
                          key={s.index}
                          disabled={s.is_yours}
                          className={`letter-btn ${picks[q.key] === s.index ? 'selected' : ''} ${s.is_yours ? 'disabled' : ''}`}
                          onClick={() => pick(q.key, s.index)}
                        >
                          {s.letter}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
                <button className="btn btn-gold btn-large" onClick={handleVote} disabled={!ready || busy}>
                  {busy ? 'Submitting…' : ready ? 'Submit votes' : 'Pick one for each question'}
                </button>
                {err && <p className="inline-error">{err}</p>}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
