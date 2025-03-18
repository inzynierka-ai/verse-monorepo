import { ReactElement } from 'react';
import { useNavigate } from '@tanstack/react-router';
import styles from './HomePage.module.scss';
import Logo from '../../pages/auth/components/Logo/Logo';
import Button from '../../common/components/Button/Button';
import Link from '../../common/components/Link/Link';
import { useAuth } from '../../common/hooks';

const HomePage = (): ReactElement => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  const handleExploreStories = () => {
    navigate({ to: '/stories' });
  };

  const handleLogin = () => {
    navigate({ to: '/login' });
  };

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <Logo className={styles.logo} />
        <h2 className={styles.tagline}>Interactive Fiction Reimagined</h2>
        <p className={styles.description}>
          Dive into immersive stories where your choices shape the narrative.
          Experience a new generation of interactive storytelling.
        </p>
        
        {isLoggedIn ? (
          <Button 
            onClick={handleExploreStories} 
            className={styles.exploreButton}
          >
            Explore Stories
          </Button>
        ) : (
          <div className={styles.authButtons}>
            <Button 
              onClick={handleLogin} 
              className={styles.loginButton}
            >
              Log In
            </Button>
            <Link to="/register">
              Create an account
            </Link>
          </div>
        )}
      </div>
      <div className={styles.background}></div>
    </div>
  );
};

export default HomePage; 