import React, { useState, useEffect, useCallback, useRef } from 'react'
import { api } from './api'
import Home from './components/Home'
import JoinRoom from './components/JoinRoom'
import Lobby from './components/Lobby'
import WritingPhase from './components/WritingPhase'
import VotingPhase from './components/VotingPhase'
import RevealScreen from './components/RevealScreen'
import LoadingState from './components/LoadingState'
import ErrorState from './components/ErrorState'

const STORAGE_KEY = 'prompt-gallery-session'

function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null
  } catch {
    return null
  }
}

function saveSession(s) {
  if (s) localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  else localStorage.removeItem(STORAGE_KEY)
}

export default function App() {
  // screen: 'home' | 'join' | 'room'
  const [screen, setScreen] = useState('home')
  const [session, setSession] = useState(null) // { code, playerId }
  const [state, setState] = useState(null)
  const [error, setError] = useState(null)
  const [prefillCode, setPrefillCode] = useState('')
  const pollRef = useRef(null)

  // Restore session / read invite link on first load.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const inviteCode = params.get('room')
    const saved = loadSession()
    if (saved && saved.code && saved.playerId) {
      setSession(saved)
      setScreen('room')
    } else if (inviteCode) {
      setPrefillCode(inviteCode.toUpperCase())
      setScreen('join')
    }
  }, [])

  const poll = useCallback(async (s) => {
    try {
      const data = await api.getState(s.code, s.playerId)
      setState(data)
      setError(null)
    } catch (e) {
      setError(e.message)
      if (e.message === 'Room not found') {
        clearSession()
      }
    }
  }, [])

  // Polling loop while in a room.
  useEffect(() => {
    if (screen !== 'room' || !session) return
    poll(session)
    pollRef.current = setInterval(() => poll(session), 1500)
    return () => clearInterval(pollRef.current)
  }, [screen, session, poll])

  function enterRoom(code, playerId) {
    const s = { code, playerId }
    saveSession(s)
    setSession(s)
    setState(null)
    setScreen('room')
    // Put room code in URL for easy sharing/refresh.
    const url = new URL(window.location)
    url.searchParams.set('room', code)
    window.history.replaceState({}, '', url)
  }

  function clearSession() {
    saveSession(null)
    setSession(null)
    setState(null)
    setScreen('home')
    const url = new URL(window.location)
    url.searchParams.delete('room')
    window.history.replaceState({}, '', url)
  }

  if (screen === 'home') {
    return <Home onCreate={enterRoom} onJoinNav={() => setScreen('join')} />
  }
  if (screen === 'join') {
    return (
      <JoinRoom
        prefillCode={prefillCode}
        onJoin={enterRoom}
        onBack={() => setScreen('home')}
      />
    )
  }

  // In a room.
  if (!state) {
    return <LoadingState message="Entering the gallery…" />
  }

  const refresh = () => poll(session)

  return (
    <div className="app-shell">
      {error && <ErrorState message={error} onDismiss={() => setError(null)} />}
      {state.phase === 'lobby' && (
        <Lobby state={state} session={session} onStart={refresh} onLeave={clearSession} />
      )}
      {state.phase === 'writing' && (
        <WritingPhase state={state} session={session} onSubmitted={refresh} />
      )}
      {state.phase === 'voting' && (
        <VotingPhase state={state} session={session} onVoted={refresh} />
      )}
      {state.phase === 'reveal' && (
        <RevealScreen state={state} session={session} onNext={refresh} onLeave={clearSession} />
      )}
    </div>
  )
}
