import { ReactElement } from 'react';
import { useAuth } from '../../../common/hooks/useAuth';
import styles from './Header.module.scss';
import { Link } from '@tanstack/react-router';
import Button from '../Button';
import { useNavigate } from '@tanstack/react-router';

export const Header = (): ReactElement => {
  const { isLoggedIn, removeCredentials } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    removeCredentials();
    navigate({ to: '/' });
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <Link to="/">Verse</Link>
        <div className={styles.authStatus}>
          {isLoggedIn ? (
            <div className={styles.userInfo}>
              <span>You are logged in</span>
              <button className={styles.logoutButton} onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <Button variant="secondary" onClick={() => navigate({ to: '/login' })}>
              Login
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
