import { ReactNode, ReactElement } from 'react';
import styles from './Container.module.scss';
import Header from '../Header';

interface ContainerProps {
  children: ReactNode;
  className?: string;
}

export const Container = ({ children, className = '' }: ContainerProps): ReactElement => {
  return (
    <main className={`${styles.container} ${className}`}>
      <Header />
      <div className={styles.content}>{children}</div>
    </main>
  );
};

export default Container;
