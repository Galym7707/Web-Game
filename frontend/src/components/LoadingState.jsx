import React from 'react'

export default function LoadingState({ message = 'Loading…' }) {
  return (
    <div className="loading-state">
      <div className="spotlight" />
      <div className="loader-ring" />
      <p>{message}</p>
    </div>
  )
}
