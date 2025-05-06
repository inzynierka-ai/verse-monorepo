# Scene Transition System

This feature implements the "Finish Scene" functionality, allowing players to complete their current scene and progress to a new one. By introducing scene status tracking (`generation_not_started`, `generating`, `active`, `completed`, `failed`), we create a clear lifecycle for scenes that enables smooth transitions and proper game state management. This system also establishes a foundation for analyzing player interactions from completed scenes.

# Implementation Tasks for Scene Transition System

## 1. Database Updates
- [x] Update the Scene model to include a status field
  ```python
  status = Column(String, default="generation_not_started", nullable=False)
  ```
- [x] Add migration script to update existing scenes with default status
- [x] Update Scene schema (Pydantic model) to include the status field

## 2. Scene Service Enhancement
- [x] Add new methods to SceneService class:
  ```python
  def fetch_latest_active_scene(self, db: Session, story_id: int) -> Optional[Scene]
  def mark_scene_completed(self, db: Session, scene_uuid: uuid.UUID, story_id: int) -> Optional[Scene]
  def process_completed_scene(self, db: Session, scene_id: int) -> None
  ```
- [x] Modify existing `fetch_latest_scene` to filter by status where appropriate

## 3. API Endpoint Implementation
- [x] Add new endpoint to mark a scene as completed:
  ```python
  @router.patch("/{story_uuid}/scenes/{scene_uuid}/complete", response_model=scene_schema.Scene)
  ```
- [x] Update existing "latest scene" endpoint to only return active scenes
- [x] Handle 404 responses properly when no active scene exists (to trigger generation)

## 4. Scene Generator Integration
- [X] Update SceneGeneratorAgent to set proper scene status during different phases:
  - Set `generation_not_started` when scene is first created
  - Set `generating` during scene generation process
  - Set `active` when generation is complete and scene is ready for play
- [X] Add error handling to set `failed` status when generation errors occur

## 5. Message Analysis Framework
- [X] Create scaffolding for message analysis in `process_completed_scene`:
  - Fetch all messages for the completed scene
  - Implement summarization logic (placeholder for now)
  - Store summary data in appropriate location

## 6. Frontend Updates
- [x] Modify SceneView to handle the "Finish Scene" button click:
  - Call the new complete endpoint
  - Navigate to GameView
- [x] Update GameView to handle scene generation when no active scene exists
  - Use 404 error from latest scene endpoint to trigger generation
  - Show appropriate loading states during generation

## 7. Testing
- [ ] Write tests for status transitions
- [ ] Test complete flow from finishing a scene to generating a new one
- [ ] Verify error handling when scene generation fails

## 8. Documentation
- [ ] Document the scene lifecycle (statuses and transitions)
- [ ] Update API documentation to reflect new endpoints
- [ ] Create developer guide for scene transition implementation
