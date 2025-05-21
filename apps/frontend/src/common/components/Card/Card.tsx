import { ReactNode, ReactElement } from 'react';
import styles from './Card.module.scss';

export interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card = ({ children, className = '', onClick }: CardProps): ReactElement => {
  return (
    <div className={`${styles.card} ${className} ${onClick ? styles.clickable : ''}`} onClick={onClick}>
      {children}
    </div>
  );
};

export default Card;
