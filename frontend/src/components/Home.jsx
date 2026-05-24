import React, { useState } from 'react'
import { api } from '../api'
import RulesPanel from './RulesPanel'

export default function Home({ onCreate, onJoinNav }) {
  const [nickname, setNickname] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)

  async function handleCreate() {
    if (busy) return
    const name = nickname.trim() || 'Host'
    setBusy(true)
    setErr(null)
    try {
      const { room_code, player_id } = await api.createRoom(name)
      onCreate(room_code, player_id)
    } catch (e) {
      setErr(e.message)
      setBusy(false)
    }
  }

  return (
    <div className="screen home">
      <div className="spotlight" />
      <div className="home-inner">
        <header className="brand">
          <p className="kicker">An A.I. Art Museum Party Game</p>
          <h1 className="title">Prompt Gallery</h1>
          <p className="subtitle">Can you tell art from algorithm?</p>
        </header>

        <div className="card glass home-card">
          <label className="field-label" htmlFor="nick">Your nickname</label>
          <input
            id="nick"
            className="text-input"
            placeholder="e.g. Curator Kim"
            maxLength={24}
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <div className="button-row">
            <button className="btn btn-gold" onClick={handleCreate} disabled={busy}>
              {busy ? 'Creating…' : 'Create Room'}
            </button>
            <button className="btn btn-ghost" onClick={onJoinNav} disabled={busy}>
              Join Room
            </button>
          </div>
          {err && <p className="inline-error">{err}</p>}
        </div>

        <RulesPanel />
      </div>
    </div>
  )
}
