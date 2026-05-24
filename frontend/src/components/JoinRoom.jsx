import React, { useState } from 'react'
import { api } from '../api'

export default function JoinRoom({ prefillCode, onJoin, onBack }) {
  const [code, setCode] = useState(prefillCode || '')
  const [nickname, setNickname] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)

  async function handleJoin() {
    if (busy) return
    const c = code.trim().toUpperCase()
    if (c.length < 3) {
      setErr('Enter a valid room code')
      return
    }
    setBusy(true)
    setErr(null)
    try {
      const { player_id, room_code } = await api.joinRoom(c, nickname.trim() || 'Player')
      onJoin(room_code, player_id)
    } catch (e) {
      setErr(e.message)
      setBusy(false)
    }
  }

  return (
    <div className="screen join">
      <div className="spotlight" />
      <div className="home-inner">
        <header className="brand small">
          <h1 className="title">Join a Room</h1>
          <p className="subtitle">Enter the gallery</p>
        </header>

        <div className="card glass home-card">
          <label className="field-label" htmlFor="code">Room code</label>
          <input
            id="code"
            className="text-input code-input"
            placeholder="ABCD"
            maxLength={4}
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
          />
          <label className="field-label" htmlFor="jnick">Your nickname</label>
          <input
            id="jnick"
            className="text-input"
            placeholder="e.g. Critic Lee"
            maxLength={24}
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
          />
          <div className="button-row">
            <button className="btn btn-gold" onClick={handleJoin} disabled={busy}>
              {busy ? 'Joining…' : 'Join Room'}
            </button>
            <button className="btn btn-ghost" onClick={onBack} disabled={busy}>
              Back
            </button>
          </div>
          {err && <p className="inline-error">{err}</p>}
        </div>
      </div>
    </div>
  )
}
