import {
  createRoute,
  createRootRoute,
  createRouter,
  RouterProvider,
  Outlet,
} from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import GameView from './pages/game/GameView/GameView';
import StoriesView from './pages/game/StoriesView/StoriesView';
import LoginView from './pages/auth/LoginView';
import RegisterView from './pages/auth/RegisterView';
import ForgotPasswordView from './pages/auth/ForgotPasswordView';
import HomePage from './pages/homepage/HomePage';
import StoryGenerationView from './pages/game/StoryGenerationView';
import SceneView from './pages/game/SceneView/SceneView';
import ChatView from './pages/game/ChatView/ChatView';

// Define a root route with layout
const rootRoute = createRootRoute({
  component: () => (
    <>
      <Outlet />
      {process.env.NODE_ENV === 'development' && <TanStackRouterDevtools />}
    </>
  ),
});

// Introduction route
const introductionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
});

// Stories route
const storiesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/stories',
  component: StoriesView,
});

// Create story route
const createStoryRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/create-story',
  component: StoryGenerationView,
});

// Game route - simplified to a single URL
export const gameRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/play/$storyId',
  component: GameView,
});

export const sceneRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/play/$storyId/scenes/$sceneId',
  component: SceneView,
});

export const chatRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/play/$storyId/scenes/$sceneId/characters/$characterId',
  component: ChatView,
});

// Login route
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginView,
});

// Register route
const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterView,
});

// Forgot password route
const forgotPasswordRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/forgot-password',
  component: ForgotPasswordView,
});

// Register all routes
const routeTree = rootRoute.addChildren([
  introductionRoute,
  gameRoute,
  sceneRoute,
  chatRoute,
  storiesRoute,
  createStoryRoute,
  loginRoute,
  registerRoute,
  forgotPasswordRoute,
]);

// Create the router using the route tree
export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
});

// Register your router for maximum type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

// Re-export the RouterProvider
export { RouterProvider };
