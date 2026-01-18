# Clean Intermediate Version (Conflict-Free)

This folder contains clean, conflict-free copies of the Intermediate AI flow so you can
test it locally without merging into your main repo.

## What’s included
- `clean-version/backend/app.py`: Flask backend with A–E heuristic sign scoring and the
  `/asl/check` endpoint (returns `Unknown` for low-confidence inputs).
- `clean-version/src/Intermediate.tsx`: Intermediate UI with A–Z prompts (A–E have
  specific guidance).
- `clean-version/src/Intermediate.css`: Styles for the Intermediate page.

## How to use
1. Copy these files into your working project:
   - `backend/app.py`
   - `src/Intermediate.tsx`
   - `src/Intermediate.css`
2. Run the backend on port **5001**:
   ```bash
   cd backend
   python app.py
   ```
3. Run the frontend:
   ```bash
   npm run dev
   ```
4. Open:
   ```
   http://localhost:5173/intermediate
   ```

If you want more letters beyond A–E to be recognized, the backend classifier needs
additional heuristics or a trained model. Right now it is intentionally limited to A–E.
