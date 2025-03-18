
import { ReactElement } from 'react';
import styles from './Logo.module.scss';

interface LogoContainerProps {
  
  className?: string;
}

export const Logo = ({ 
  className = '' 
}: LogoContainerProps): ReactElement => {
  return (
    <div className={`${styles.logoContainer} ${className}`}>
      <h1>VERSE</h1>
    </div>
  );
};

export default Logo;
