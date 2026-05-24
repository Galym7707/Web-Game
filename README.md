# Prompt Gallery

A multiplayer browser party game where friends enter an AI art museum, look at a real
public-domain artwork, write or defend interpretations, and vote to discover which statement
was written by the real curator, by an AI, or by a bluffing player.

> Can you tell art from algorithm?

## Game mechanics

Everyone in the room sees the **same artwork**. The secret isn't in the image — it's in your
role. Each player writes one short interpretation (max 180 chars), then everyone votes on three
questions: which statement is the real curator's, which one was written by AI, and which is the
best bluff. Then the reveal shows who was who, plus scores.

## Roles

- **Real Curator** — gets private curator notes and writes the true interpretation in their own words.
- **AI Defender** — gets an AI-written statement and must rewrite it so nobody spots the machine.
- **Fake Critic** — gets no real meaning and must invent a believable interpretation. With 4+ players there are several.

3–6 players recommended (minimum 3).

## Tech stack

- **Frontend:** React + Vite, plain CSS (dark glassmorphism museum theme).
- **Backend:** FastAPI + Python, in-memory room storage, HTTP polling (no WebSocket, no database, no auth).
- **External APIs:** Art Institute of Chicago (artworks), Google Gemini (optional content generation).
- **Deploy:** Single Docker image — FastAPI serves the built React app.

## AI usage

When a Gemini key is present, the backend asks Gemini (vision model) to generate the curator
notes, the AI statement, mood words, visual anchors, an exhibition title, and a critic review
for each artwork.

### Why it works without external AI

If no Gemini key is set — or Gemini/Art Institute fail — the game falls back to a local content
generator and locally generated SVG artworks. **Every feature works offline.** Gemini only makes
the content richer; it is never required.

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `GEMINI_API_KEY` | Gemini key (or use `GOOGLE_API_KEY`) | No |
| `GOOGLE_API_KEY` | Alternative name for the Gemini key | No |
| `PORT` | Port to listen on (defaults to 7860) | No |

Copy `.env.example` to `.env` for local use. **Never commit `.env` or a real key.**

## Run locally

Backend:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 7860
```

Frontend (separate terminal — Vite proxies `/api` to port 7860):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

To run the production build in one process:

```bash
cd frontend && npm install && npm run build && cd ..
uvicorn backend.main:app --port 7860   # serves the built app at http://localhost:7860
```

Or with Docker:

```bash
docker build -t prompt-gallery .
docker run -p 7860:7860 -e GEMINI_API_KEY=your_key prompt-gallery
```

## Hugging Face deployment

The repo is a Hugging Face **Docker Space** out of the box (listens on `0.0.0.0:$PORT`, defaults to 7860).

1. Point a Docker Space at this repo (or push the files to the Space).
2. In **Space → Settings → Secrets**, add `GEMINI_API_KEY` with your key.
   Do **not** put the key in code or in the Dockerfile.
3. The Space builds the Docker image and serves the game.

Target Space: https://huggingface.co/spaces/Galym7707/Web-Game

## Demo checklist

- [ ] Open the site, enter a nickname, **Create Room**.
- [ ] Copy the invite link, open it in another browser/device, **Join**.
- [ ] With 3+ players, host clicks **Start Round**.
- [ ] Read your private role, write a statement, submit.
- [ ] Vote on the three questions.
- [ ] See the reveal, scores, and the real artwork metadata.
- [ ] Click **Play Again**.
