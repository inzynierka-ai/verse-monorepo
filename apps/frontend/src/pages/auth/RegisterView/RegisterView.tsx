import { useState, FormEvent } from 'react';
import { Link } from '@tanstack/react-router';
import styles from '../styles/auth.module.scss';
import { useRegister, RegisterCredentials } from '../../../services/api';

interface RegisterViewProps {
  onRegisterSuccess?: () => void;
}

const RegisterView = ({ onRegisterSuccess }: RegisterViewProps) => {
  const [formData, setFormData] = useState<RegisterCredentials>({
    username: '',
    email: '',
    password: '',
  });

  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Partial<RegisterCredentials & { confirmPassword: string }>>(
    {},
  );
  const [registerError, setRegisterError] = useState<string | null>(null);

  const { mutate: register, isPending: isLoading } = useRegister();

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterCredentials & { confirmPassword: string }> = {};

    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    // Clear error when user types
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear register error when user makes changes
    if (registerError) {
      setRegisterError(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setRegisterError(null);

    register(formData, {
      onSuccess: () => {
        if (onRegisterSuccess) {
          onRegisterSuccess();
        }
        // Redirect to login or handle success in your app
      },
      onError: (error) => {
        setRegisterError(
          error instanceof Error ? error.message : 'Registration failed. Please try again.',
        );
      },
    });
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <div className={styles.logoContainer}>
          <h1>VERSE</h1>
        </div>

        <h2 className={styles.title}>Join the Adventure</h2>
        <p className={styles.subtitle}>Create your account to begin your journey</p>

        {registerError && <div className={styles.error}>{registerError}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label htmlFor="username" className={styles.label}>
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className={styles.input}
              placeholder="Choose a username"
              disabled={isLoading}
            />
            {errors.username && <div className={styles.error}>{errors.username}</div>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={styles.input}
              placeholder="Enter your email"
              disabled={isLoading}
            />
            {errors.email && <div className={styles.error}>{errors.email}</div>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.label}>
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={styles.input}
              placeholder="Create a password"
              disabled={isLoading}
            />
            {errors.password && <div className={styles.error}>{errors.password}</div>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword" className={styles.label}>
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={confirmPassword}
              onChange={handleChange}
              className={styles.input}
              placeholder="Confirm your password"
              disabled={isLoading}
            />
            {errors.confirmPassword && <div className={styles.error}>{errors.confirmPassword}</div>}
          </div>

          <button type="submit" className={styles.button} disabled={isLoading}>
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className={styles.linkContainer}>
          Already have an account?
          <Link to="/login" className={styles.link}>
            Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterView;
