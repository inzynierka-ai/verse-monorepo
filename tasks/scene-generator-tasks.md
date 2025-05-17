# Scene Generator Tasks

The goal of this task is to connect the scene generator agent with the frontend in the game view.


1. **Backend: Read-only “latest” endpoint**  
   - GET `/stories/{storyId}/scene/latest`  
     • If a complete scene exists → return it (200 + payload).  
     • Else → return 404 (no scheduling or side-effects).  

2. **Backend: Single WS endpoint for generate & stream**  
   - WS `/api/game/ws/stories/{storyId}/scene`  
     • On connect, load from DB:  
       – If scene complete → `ws.send_json({ type: 'SCENE_COMPLETE', payload: scene })` and optionally keep open for chat.  
       – Else → instantiate `SceneGeneratorAgent` inline and drive it over the socket:  
         • After each tool step, `ws.send_json({ type: 'LOCATION_ADDED', payload: {...} })`, or `CHARACTER_ADDED`, etc.  
         • When finalized → persist full scene to DB and send `SCENE_COMPLETE`.  
     • On disconnect → cancel/cleanup agent if still running.  

3. **Frontend: New `useSceneGeneration` hook**  
   - Mirror `useStoryGeneration.ts` but for scenes:  
     • Connect to `/api/game/ws/stories/{storyId}/scene`.  
     • Expose `state: { status, lastLocation?, lastCharacters[], description?, error? }`.  
     • Expose `start()` (no payload, WS URL encodes storyId so server knows what to do).  
     • Handle messages by type and merge into state.  

4. **Frontend: Refactor `GameView.tsx`**  
   - Remove `useScene`/`useMessages`.  
   - On mount: call GET `/latest`.  
     • 200 → render full scene immediately.  
     • 404 → call `start()` on the new hook.  
   - Subscribe to the hook’s state:  
     • While `status==='connecting' | 'generating'`: show skeletons/placeholders.  
     • As each `LOCATION_ADDED` or `CHARACTER_ADDED` arrives: render its card immediately.  
     • On `SCENE_COMPLETE`: show final description and enable chat input.  

5. **Error handling & retries**  
   - WS reconnect logic in the hook (as in `useStoryGeneration`).  
   - If agent errors mid-stream → send `{ type:'ERROR', payload:{message} }` → hook sets `status='error'`.  
   - Expose a “retry” in `GameView` to restart WS and re-generate if needed.  

6. **Testing & docs**  
   - **Backend**: unit tests for WS handler (mock agent emits).  
   - **Frontend**: unit tests for `useSceneGeneration` message handling and reconnect.  
   - Update README to describe:  
     1. GET 404 → WS generate/stream flow  
     2. message types and payload shapes  

Each piece can be its own PR. Which one shall we start with?
