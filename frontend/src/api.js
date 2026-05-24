// Same-origin in production; Vite proxy handles /api in dev.
const BASE = ''

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      const data = await res.json()
      detail = data.detail || detail
    } catch (e) { /* ignore */ }
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  createRoom: (nickname) =>
    req('/api/rooms', { method: 'POST', body: JSON.stringify({ nickname }) }),

  joinRoom: (code, nickname) =>
    req(`/api/rooms/${code}/join`, {
      method: 'POST',
      body: JSON.stringify({ nickname }),
    }),

  getState: (code, playerId) =>
    req(`/api/rooms/${code}/state?player_id=${encodeURIComponent(playerId)}`),

  start: (code, playerId) =>
    req(`/api/rooms/${code}/start`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId }),
    }),

  submit: (code, playerId, text) =>
    req(`/api/rooms/${code}/submit`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, text }),
    }),

  vote: (code, playerId, real, ai, bluff) =>
    req(`/api/rooms/${code}/vote`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, real, ai, bluff }),
    }),

  nextRound: (code, playerId) =>
    req(`/api/rooms/${code}/next-round`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId }),
    }),

  reset: (code, playerId) =>
    req(`/api/rooms/${code}/reset`, {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId }),
    }),
}
