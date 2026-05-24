import React from 'react'

export default function ErrorState({ message, onDismiss }) {
  return (
    <div className="error-toast" role="alert">
      <span>{message}</span>
      {onDismiss && (
        <button className="error-close" onClick={onDismiss} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
  )
}
