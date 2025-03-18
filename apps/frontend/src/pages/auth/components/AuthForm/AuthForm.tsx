import { FormEvent, ReactElement, ReactNode } from 'react';
import styles from './AuthForm.module.scss';

interface AuthFormProps {
  children: ReactNode;
  className?: string;
  onSubmit?: (e: FormEvent<HTMLFormElement>) => void;
}

export const AuthForm = ({ 
  children, 
  className = '',
  onSubmit
}: AuthFormProps): ReactElement => {
  return (
    <form className={`${styles.form} ${className}`} onSubmit={onSubmit}>
      {children}
    </form>
  );
};

export default AuthForm;
