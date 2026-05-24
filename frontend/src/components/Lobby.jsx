import React, { useState } from 'react'
import { api } from '../api'
import RulesPanel from './RulesPanel'

export default function Lobby({ state, session, onStart, onLeave }) {
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState(false)
  const [err, setErr] = useState(null)

  const canStart = state.player_count >= 3
  const inviteLink = `${window.location.origin}/?room=${state.code}`

  function copyInvite() {
    navigator.clipboard.writeText(inviteLink).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    }).catch(() => setErr('Copy failed — link is shown above'))
  }

  async function handleStart() {
    if (busy) return
    setBusy(true)
    setErr(null)
    try {
      await api.start(state.code, session.playerId)
      onStart()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="screen lobby">
      <div className="spotlight" />
      <div className="lobby-inner">
        <header className="brand small">
          <h1 className="title">Prompt Gallery</h1>
          <p className="subtitle">Lobby</p>
        </header>

        <div className="card glass">
          <div className="room-code-row">
            <div>
              <p className="field-label">Room code</p>
              <p className="room-code">{state.code}</p>
            </div>
            <button className="btn btn-gold" onClick={copyInvite}>
              {copied ? 'Link copied!' : 'Copy invite link'}
            </button>
          </div>
          <p className="invite-hint">{inviteLink}</p>
        </div>

        <div className="card glass">
          <h3 className="section-title">Players ({state.player_count})</h3>
          <ul className="player-list">
            {state.players.map((p) => (
              <li key={p.id} className="player-chip">
                <span className="dot" />
                {p.name}
                {p.id === state.host_id && <span className="host-tag">host</span>}
                {p.id === session.playerId && <span className="you-tag">you</span>}
              </li>
            ))}
          </ul>
        </div>

        {state.is_host ? (
          <div className="card glass">
            <button className="btn btn-gold btn-large" onClick={handleStart} disabled={!canStart || busy}>
              {busy ? 'Starting…' : canStart ? 'Start Round' : 'Need at least 3 players'}
            </button>
            {!canStart && <p className="waiting-text">Waiting for more players to join…</p>}
          </div>
        ) : (
          <div className="card glass">
            <p className="waiting-text">Waiting for the host to start the round…</p>
          </div>
        )}

        <RulesPanel compact />

        <button className="btn btn-text" onClick={onLeave}>Leave room</button>
        {err && <p className="inline-error">{err}</p>}
      </div>
    </div>
  )
}
