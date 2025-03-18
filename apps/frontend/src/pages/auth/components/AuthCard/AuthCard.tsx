import { ReactNode, ReactElement } from 'react';
import styles from './AuthCard.module.scss';
import { Logo } from '../index';
import { Card } from '@/common/components/Card';

interface AuthCardProps {
  title: string;
  subtitle?: string;
  errorMessage?: string | null;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export const AuthCard = ({
  title,
  subtitle,
  errorMessage,
  children,
  footer,
  className = ''
}: AuthCardProps): ReactElement => {
  return (
    <Card className={className}>
      <Logo />
      
      <h2 className={styles.title}>{title}</h2>
      
      {subtitle && (
        <p className={styles.subtitle}>{subtitle}</p>
      )}
      
      {errorMessage && (
        <div className={styles.error}>{errorMessage}</div>
      )}
      
      {children}
      
      {footer && (
        <div className={styles.linkContainer}>
          {footer}
        </div>
      )}
    </Card>
  );
};

export default AuthCard;
