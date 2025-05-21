import { ReactElement, useState, useRef, useEffect } from 'react';
import styles from './HamburgerMenu.module.scss';
import Button from '../Button';

interface HamburgerMenuProps {
  onLogout: () => void;
}

export const HamburgerMenu = ({ onLogout }: HamburgerMenuProps): ReactElement => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleLogout = () => {
    onLogout();
    setMenuOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className={styles.menuContainer} ref={menuRef}>
      <button className={styles.hamburgerButton} onClick={toggleMenu}>
        <div className={`${styles.hamburgerIcon} ${menuOpen ? styles.open : ''}`}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>
      {menuOpen && (
        <div className={styles.dropdown}>
          <Button variant="danger" onClick={handleLogout} className={styles.logoutButton}>
            Logout
          </Button>
        </div>
      )}
    </div>
  );
};

export default HamburgerMenu;
