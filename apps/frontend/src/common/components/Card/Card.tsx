import { ReactNode, ReactElement } from 'react';
import styles from './Card.module.scss';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export const Card = ({
  children,
  className = ''
}: CardProps): ReactElement => {
  return (
      <div className={`${styles.card} ${className}`}>
        {children}
      </div>
  );
};

export default Card;
