import { ReactNode } from 'react';
import { Link as RouterLink } from '@tanstack/react-router';
import styles from './Link.module.scss';

interface LinkProps {
  children: ReactNode;
  external?: boolean;
  className?: string;
  to: string;
  [key: string]: any;
}

export const Link = ({
  children,
  external = false,
  className = '',
  to,
  ...props
}: LinkProps) => {
  if (external) {
    return (
      <a 
        className={`${styles.link} ${className}`}
        href={to}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    );
  }

  return (
    <RouterLink 
      className={`${styles.link} ${className}`}
      to={to}
      {...props}
    >
      {children}
    </RouterLink>
  );
};

export default Link; 