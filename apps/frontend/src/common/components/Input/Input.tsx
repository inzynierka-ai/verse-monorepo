import { InputHTMLAttributes, ReactElement } from 'react';
import styles from './Input.module.scss';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

const Input = ({
  label,
  error,
  fullWidth = false,
  className = '',
  ...props
}: InputProps): ReactElement => {
  return (
    <div className={`${styles.formGroup} ${fullWidth ? styles.fullWidth : ''}`}>
      {label && (
        <label className={styles.label} htmlFor={props.id}>
          {label}
        </label>
      )}
      <input 
        className={`${styles.input} ${error ? styles.hasError : ''} ${className}`} 
        {...props} 
      />
      {error && <div className={styles.error}>{error}</div>}
    </div>
  );
};

export default Input;
