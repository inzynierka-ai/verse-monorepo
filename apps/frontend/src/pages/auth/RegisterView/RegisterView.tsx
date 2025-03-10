import { useState, FormEvent } from 'react';
import { Link } from '@/common/components/Link';
import { AuthCard, AuthForm } from '../components';
import { useRegister, RegisterCredentials } from '@/services/api';
import Button from '@/common/components/Button';
import Input from '@/common/components/Input';

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

  const footerContent = (
    <>
      Already have an account?
      <Link to="/login">Login</Link>
    </>
  );

  return (
    <AuthCard 
      title="Join the Adventure"
      subtitle="Create your account to begin your journey"
      errorMessage={registerError}
      footer={footerContent}
    >
      <AuthForm onSubmit={handleSubmit}>
        <Input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Choose a username"
          disabled={isLoading}
          label="Username"
          error={errors.username}
          fullWidth
        />

        <Input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Enter your email"
          disabled={isLoading}
          label="Email"
          error={errors.email}
          fullWidth
        />

        <Input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Create a password"
          disabled={isLoading}
          label="Password"
          error={errors.password}
          fullWidth
        />

        <Input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={confirmPassword}
          onChange={handleChange}
          placeholder="Confirm your password"
          disabled={isLoading}
          label="Confirm Password"
          error={errors.confirmPassword}
          fullWidth
        />

        <Button type="submit" disabled={isLoading} fullWidth>
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </Button>
      </AuthForm>
    </AuthCard>
  );
};

export default RegisterView;
