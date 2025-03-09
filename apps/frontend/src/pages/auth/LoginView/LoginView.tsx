import { useState, FormEvent } from 'react';
import { Link } from '@tanstack/react-router';
import styles from '../styles/auth.module.scss';
import { useLogin, LoginCredentials } from '../../../services/api';
import { useNavigate } from '@tanstack/react-router';
interface LoginViewProps {
  onLoginSuccess?: () => void;
}

const LoginView = ({ onLoginSuccess }: LoginViewProps) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginCredentials>({
    username: '',
    password: '',
  });

  const [errors, setErrors] = useState<Partial<LoginCredentials>>({});
  const [loginError, setLoginError] = useState<string | null>(null);

  const { mutate: login, isPending: isLoading } = useLogin();

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginCredentials> = {};

    if (!formData.username) {
      newErrors.username = 'Username is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user types
    if (errors[name as keyof LoginCredentials]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear login error when user makes changes
    if (loginError) {
      setLoginError(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
  
    if (!validateForm()) {
      return;
    }
  
    setLoginError(null);
  
    login(formData, {
      onSuccess: () => {
        if (onLoginSuccess) {
          onLoginSuccess();
        }
        navigate({ to: '/stories' });
      },
      onError: (error) => {
        setLoginError(
          error instanceof Error ? error.message : 'Invalid username or password. Please try again.',
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

        <h2 className={styles.title}>Welcome Back</h2>
        <p className={styles.subtitle}>Enter your credentials to continue your journey</p>

        {loginError && <div className={styles.error}>{loginError}</div>}

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
              placeholder="Enter your username"
              disabled={isLoading}
            />
            {errors.username && <div className={styles.error}>{errors.username}</div>}
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
              placeholder="Enter your password"
              disabled={isLoading}
            />
            {errors.password && <div className={styles.error}>{errors.password}</div>}
          </div>

          <div className={styles.forgotPassword}>
            <Link to="/forgot-password" className={styles.link}>
              Forgot password?
            </Link>
          </div>

          <button type="submit" className={styles.button} disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className={styles.linkContainer}>
          Don't have an account?
          <Link to="/register" className={styles.link}>
            Register
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginView;