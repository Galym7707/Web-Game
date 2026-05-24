import React, { useState } from 'react'
import { api } from '../api'
import Scoreboard from './Scoreboard'

const ROLE_TAG = {
  curator: 'role-curator',
  ai_defender: 'role-ai',
  fake_critic: 'role-critic',
}

export default function RevealScreen({ state, session, onNext, onLeave }) {
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)
  const reveal = state.reveal
  const meta = state.artwork_meta

  async function handleNext() {
    if (busy) return
    setBusy(true)
    setErr(null)
    try {
      await api.nextRound(state.code, session.playerId)
      onNext()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="screen reveal">
      <div className="spotlight" />
      <div className="reveal-inner">
        <header className="brand small">
          <h1 className="title">The Reveal</h1>
          <p className="subtitle">Round {state.round_number}</p>
        </header>

        <div className="card glass critic-review">
          <p className="critic-quote">“{reveal.critic_review}”</p>
          <p className="critic-by">— The Gallery Critic</p>
        </div>

        <div className="reveal-cards">
          {reveal.cards.map((c) => (
            <div key={c.index} className={`reveal-card glass ${ROLE_TAG[c.role]}`}>
              <div className="reveal-card-head">
                <span className="statement-letter">{c.letter}</span>
                <div className="reveal-badges">
                  {c.is_real_curator && <span className="badge gold">Real Curator</span>}
                  {c.is_ai && <span className="badge cyan">AI</span>}
                  {c.is_best_bluff && <span className="badge purple">Best Bluff</span>}
                </div>
              </div>
              <p className="statement-text">{c.text}</p>
              <div className="reveal-author">
                <span className="author-name">{c.author_name}</span>
                <span className="author-role">{c.role_label}</span>
              </div>
              <div className="vote-tallies">
                <span title="Voted as real curator">👑 {c.real_votes}</span>
                <span title="Voted as AI">🤖 {c.ai_votes}</span>
                <span title="Voted best bluff">🎭 {c.bluff_votes}</span>
              </div>
            </div>
          ))}
        </div>

        <Scoreboard scores={state.scores} roundScores={reveal.round_scores} you={session.playerId} />

        <div className="card glass artwork-meta">
          <h3 className="section-title">The actual artwork</h3>
          <p className="meta-line"><strong>{meta.title}</strong></p>
          <p className="meta-line">{meta.artist}{meta.date ? ` · ${meta.date}` : ''}</p>
          <p className="meta-line subtle">{meta.source}</p>
          <p className="meta-line subtle">
            Content by: {state.content_source === 'gemini' ? 'Gemini AI' : 'local generator'}
          </p>
        </div>

        {state.is_host ? (
          <button className="btn btn-gold btn-large" onClick={handleNext} disabled={busy}>
            {busy ? 'Loading next artwork…' : 'Play Again'}
          </button>
        ) : (
          <p className="waiting-text">Waiting for the host to start the next round…</p>
        )}
        <button className="btn btn-text" onClick={onLeave}>Leave room</button>
        {err && <p className="inline-error">{err}</p>}
      </div>
    </div>
  )
}
