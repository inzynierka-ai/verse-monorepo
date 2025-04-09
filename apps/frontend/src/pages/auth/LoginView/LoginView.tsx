import { useState, FormEvent } from 'react';
import { Link } from '@/common/components/Link';
import { AuthCard, AuthForm } from '../components';
import { useLogin, LoginCredentials } from '@/services/api';
import { useNavigate } from '@tanstack/react-router';
import Button from '@/common/components/Button';
import Input from '@/common/components/Input';
import styles from './LoginView.module.scss';
import { useAuth } from '@/common/hooks';

const LoginView = () => {
  const navigate = useNavigate();
  const { saveCredentials } = useAuth();
  const [formData, setFormData] = useState<LoginCredentials>({
    username: '',
    password: '',
  });

  const [errors, setErrors] = useState<Partial<LoginCredentials>>({});
  const [loginError, setLoginError] = useState<string | null>(null);

  const { mutate: loginMutation, isPending: isLoading } = useLogin();

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

    loginMutation(formData, {
      onSuccess: (data) => {
        saveCredentials(data.token);
        navigate({ to: '/stories' });
      },
      onError: (error) => {
        setLoginError(error instanceof Error ? error.message : 'Invalid username or password. Please try again.');
      },
    });
  };

  return (
    <AuthCard 
      title="Login" 
      subtitle="Welcome back! Please enter your credentials to access your account."
      errorMessage={loginError}
      footer={
        <span>
          Don't have an account?
          <Link to="/register">Register</Link>
        </span>
      }
    >
      <AuthForm onSubmit={handleSubmit}>
        <Input
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Enter your username"
          disabled={isLoading}
          label="Username"
          error={errors.username}
          fullWidth
        />

        <Input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter your password"
          disabled={isLoading}
          label="Password"
          error={errors.password}
          fullWidth
        />

        <div className={styles.forgotPassword}>
          <Link to="/forgot-password">
            Forgot password?
          </Link>
        </div>

        <Button type="submit" disabled={isLoading} fullWidth>
          {isLoading ? 'Logging in...' : 'Login'}
        </Button>
      </AuthForm>
    </AuthCard>
  );
};

export default LoginView;