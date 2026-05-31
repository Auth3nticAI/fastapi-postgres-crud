# Week 4 Reflection

## 1. What is the difference between the SQLAlchemy model and the Pydantic schema?

The SQLAlchemy model (`models.Book`) describes the **database row** — column names, types, constraints, indexes. It exists so the ORM knows how to map between Python objects and Postgres tables.

The Pydantic schemas (`schemas.BookCreate`, `BookUpdate`, `BookResponse`) describe the **shape of data crossing the HTTP boundary** — what a client may send, what they may update, what they receive back. They validate request bodies and serialize responses.

They look similar because they're describing the same domain object (a Book), but they answer different questions: *how is it stored* vs. *how is it transmitted*. Keeping them separate means I can have an internal `created_at` column without exposing it in a response, or accept a partial `BookUpdate` that wouldn't be valid as a full DB insert.

## 2. What does `Depends(get_db)` do? Why does every endpoint need it?

`Depends(get_db)` is FastAPI's dependency injection — for each request, FastAPI calls `get_db()`, hands the yielded `Session` to the endpoint, and then runs the `finally:` block to close the session after the response is sent.

Every endpoint needs it because:
- Sessions are **per-request**. Sharing one global session across requests would interleave transactions and corrupt state under concurrency.
- The `try / yield / finally` pattern guarantees the connection is returned to the pool even if the endpoint raises.

It's the database equivalent of "open the file, do work, close the file" — abstracted so I never have to think about the close.

## 3. When you restarted the server and your data was still there — how does that feel compared to storing data in a Python list?

The Python-list version was a toy: every restart wiped everything, every concurrent request risked race conditions, and nothing would scale past one process. The Postgres version is the first time the API has felt like *a real system* — the data has an existence independent of the process serving it.

Architecturally, the big shift is that the API is no longer the source of truth. It's a thin layer that translates HTTP requests into SQL, with the actual state living in a separate process (Postgres) that I can query directly, back up, replicate, or connect a different frontend to. The database becomes the contract; the API becomes a view onto it.

## 4. What was the most confusing part of connecting the frontend to the backend?

Two things that weren't obvious from the lab spec:

- **Host consistency.** I set `NEXT_PUBLIC_API_URL=http://localhost:8000` and bound uvicorn to `127.0.0.1`. Most of the time these are interchangeable, but when a headless browser hit the page at `http://127.0.0.1:3000`, the bundle still sent fetches to `localhost:8000` — and the `Origin` header was `127.0.0.1:3000`, which wasn't on the CORS whitelist. Symptom looked like a totally silent fetch failure. Lesson: pick one hostname and use it everywhere — env, server bind address, and CORS allowlist all the way through.

- **Next 16's `allowedDevOrigins`.** Next's dev server blocks cross-origin requests to its own dev resources (HMR WebSocket) by default. Hitting the dev server from a non-allowed host (anything other than `localhost`) breaks HMR loudly in the console but, in my case, also kept React from re-rendering after `setState`. Fix: add `allowedDevOrigins: ['127.0.0.1']` to `next.config.ts`. Took me a debug session with Playwright + request logging to track this down.

## 5. When does CORS become a problem and why? In your own words.

CORS kicks in any time a browser makes a request from one origin (scheme + host + port) to a different origin. The browser asks the server: *"are you OK with `https://app.example.com` reading your response?"* If the server doesn't return an `Access-Control-Allow-Origin` header that matches, the browser blocks the response from JavaScript — the request still hits the server, but your code can't see what came back.

Cases where it bites:
- **Different ports** count as different origins. `localhost:3000` ↔ `localhost:8000` is a CORS boundary, even though they're "the same machine."
- **Different hostnames** for the same machine count too — `localhost` ↔ `127.0.0.1` is also a CORS boundary, which is why my mixed-host setup broke.
- **Preflighted requests** (anything with custom headers like `Content-Type: application/json`, or non-`GET`/`POST`/`HEAD` methods) trigger an extra `OPTIONS` round-trip that also has to be allowed.

It's not a security mechanism that the server *enforces* — it's a contract the browser enforces on JS calls based on what the server says is OK. So when you control both sides (your own FastAPI talking to your own Next.js), the fix is just to whitelist the right origins on the server, which is what `CORSMiddleware` does for me here.

## 6. What is the difference between `useEffect` with `[]` and without it?

Both run the effect after the component renders. The dependency array controls when it runs *again*:

- **`useEffect(fn, [])`** — runs once after the first render, then never again (until the component unmounts and remounts). This is what I want for "fetch the list of books on mount."
- **`useEffect(fn)`** (no array) — runs after *every* render. If the effect calls `setState`, that triggers another render, which triggers the effect again, which triggers another render. Infinite loop. Almost always a bug.
- **`useEffect(fn, [someValue])`** — runs after the first render, then again any time `someValue` changes between renders. I use this in the detail page with `[bookId]` so the effect re-fetches if the route param changes.

There's also React 18+ strict-mode dev behavior where effects with `[]` run twice (mount → cleanup → mount) to surface bugs around cleanup. That's why I have a `cancelled` flag inside the effect — so a stale fetch from the first run can't `setState` and overwrite fresher data from the second run.
