import { ReactNode, ReactElement } from 'react';
import styles from './Container.module.scss';

interface ContainerProps {
  children: ReactNode;
  className?: string;
}

export const Container = ({
  children,
  className = ''
}: ContainerProps): ReactElement => {
  return (
    <div className={`${styles.container} ${className}`}>
      {children}
    </div>
  );
};

export default Container;
