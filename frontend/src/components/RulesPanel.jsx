import React from 'react'

export default function RulesPanel({ compact }) {
  return (
    <div className={`rules-panel ${compact ? 'compact' : ''}`}>
      <h3>How it works</h3>
      <ul>
        <li>Everyone sees the same artwork.</li>
        <li>One player knows the real curator notes.</li>
        <li>One player receives an AI-style interpretation.</li>
        <li>Everyone else invents believable fake meanings.</li>
        <li>Write your statement, vote, and find out who fooled the gallery.</li>
      </ul>
    </div>
  )
}
