import React, { useState } from 'react'
import { api } from '../api'
import ArtworkStage from './ArtworkStage'
import RoleCard from './RoleCard'

const MAX = 180

export default function WritingPhase({ state, session, onSubmitted }) {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)

  const submitted = state.submitted

  async function handleSubmit() {
    if (busy || submitted) return
    if (!text.trim()) {
      setErr('Write something first')
      return
    }
    setBusy(true)
    setErr(null)
    try {
      await api.submit(state.code, session.playerId, text.trim())
      onSubmitted()
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
          <RoleCard task={state.your_task} />

          {submitted ? (
            <div className="card glass waiting-card">
              <h3>Statement submitted ✓</h3>
              <p className="waiting-text">
                Waiting for other players… ({state.submitted_count}/{state.player_count})
              </p>
              <div className="mini-progress">
                <div className="mini-bar" style={{ width: `${(state.submitted_count / state.player_count) * 100}%` }} />
              </div>
            </div>
          ) : (
            <div className="card glass">
              <h3 className="section-title">Write your interpretation</h3>
              <ul className="writing-rules">
                <li>Write in your own words.</li>
                <li>Max 180 characters. Sound human.</li>
                <li>Don't mention the real artist or title.</li>
                <li>Make it feel like an interpretation, not a list.</li>
              </ul>
              <textarea
                className="statement-input"
                maxLength={MAX}
                rows={4}
                placeholder="This piece feels like…"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              <div className="char-row">
                <span className={text.length >= MAX ? 'char-max' : ''}>
                  {text.length}/{MAX}
                </span>
                <button className="btn btn-gold" onClick={handleSubmit} disabled={busy}>
                  {busy ? 'Submitting…' : 'Submit statement'}
                </button>
              </div>
              {err && <p className="inline-error">{err}</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
