
import { ReactElement } from 'react';
import styles from './Logo.module.scss';

interface LogoContainerProps {
  width?: number;
  height?: number;
  className?: string;
  inline?: boolean;
}

export const Logo = ({ className = '', width = 40, height = 40, inline = false }: LogoContainerProps): ReactElement => {
  return (
    <div className={`${styles.logoContainer} ${className}`}>
      {inline ? (
        <img src="/logo-inline.png" alt="Verse" width={width} height={height} />
      ) : (
        <img src="/logo.png" alt="Verse" width={width} height={height} />
      )}
    </div>
  );
};

export default Logo;
