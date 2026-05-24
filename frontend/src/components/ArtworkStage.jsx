import React, { useState } from 'react'

export default function ArtworkStage({ artwork, round }) {
  const [loaded, setLoaded] = useState(false)
  if (!artwork) return null
  return (
    <div className="artwork-stage">
      <div className="exhibition-plate">
        <span className="round-pill">Round {round}</span>
        <h2 className="exhibition-title">{artwork.exhibition_title}</h2>
      </div>
      <div className="frame">
        {!loaded && <div className="frame-skeleton" />}
        <img
          className={`artwork-img ${loaded ? 'show' : ''}`}
          src={artwork.image_url}
          alt="Artwork on display"
          onLoad={() => setLoaded(true)}
          onError={() => setLoaded(true)}
        />
      </div>
      <p className="source-line">{artwork.source}</p>
    </div>
  )
}
