import { ReactElement } from 'react';
import { useAuth } from '../../../common/hooks/useAuth';
import styles from './Header.module.scss';
import { Link } from '@tanstack/react-router';

export const Header = (): ReactElement => {
  const { isLoggedIn, removeCredentials } = useAuth();

  console.log(isLoggedIn);

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <Link to="/">Verse</Link>
        <div className={styles.authStatus}>
          {isLoggedIn ? (
            <div className={styles.userInfo}>
              <span>You are logged in</span>
              <button className={styles.logoutButton} onClick={removeCredentials}>
                Logout
              </button>
            </div>
          ) : (
            <span>You are not logged in</span>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
