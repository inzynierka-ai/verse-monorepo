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
import ChaptersView from './pages/game/ChaptersView';
import ChapterView from './pages/game/ChapterView';
import LoginView from './pages/auth/LoginView';
import RegisterView from './pages/auth/RegisterView';
import ForgotPasswordView from './pages/auth/ForgotPasswordView';
import { IntroductionWrapper } from './components/IntroductionWrapper';

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
  component: IntroductionWrapper,
});

// Game route
export const gameRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/stories/$storyId/chapter/$chapterId/scene/$sceneId',
  component: GameView,
});

// Stories route
const storiesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/stories',
  component: StoriesView,
});

// Create story chapters route
export const storyChaptersRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'stories/$storyId/chapters',
  component: ChaptersView,
});

// Create chapter detail route
export const chapterDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'stories/$storyId/chapter/$chapterId',
  component: ChapterView,
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
  storiesRoute,
  storyChaptersRoute,
  chapterDetailRoute,
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
