import { useState, FormEvent } from 'react';
import { Link } from '@/common/components/Link';
import { useForgotPassword, ForgotPasswordRequest } from '@/services/api';
import Button from '@/common/components/Button';
import Input from '@/common/components/Input';
import { AuthCard, AuthForm } from '../components';
import styles from './ForgotPasswordView.module.scss';

const ForgotPasswordView = () => {
  const [formData, setFormData] = useState<ForgotPasswordRequest>({
    email: '',
  });

  const [errors, setErrors] = useState<Partial<ForgotPasswordRequest>>({});
  const [requestError, setRequestError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const { mutate: forgotPassword, isPending: isLoading } = useForgotPassword();

  const validateForm = (): boolean => {
    const newErrors: Partial<ForgotPasswordRequest> = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
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
    if (errors[name as keyof ForgotPasswordRequest]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear request error when user makes changes
    if (requestError) {
      setRequestError(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setRequestError(null);

    forgotPassword(formData, {
      onSuccess: () => {
        setIsSubmitted(true);
      },
      onError: (error) => {
        setRequestError(
          error instanceof Error
            ? error.message
            : 'Password reset request failed. Please try again.',
        );
      },
    });
  };

  const subtitle = isSubmitted
    ? 'Check your email for password reset instructions'
    : 'Enter your email to receive password reset instructions';

  const footerContent = (
    <>
      Remember your password?
      <Link to="/login">Login</Link>
    </>
  );

  return (
    <AuthCard 
      title="Reset Password"
      subtitle={subtitle}
      errorMessage={requestError}
      footer={footerContent}
    >
      {isSubmitted ? (
        <div className={styles.successMessage}>
          Password reset instructions have been sent to your email. Please check your inbox and
          follow the instructions to reset your password.
        </div>
      ) : (
        <AuthForm onSubmit={handleSubmit}>
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

          <Button type="submit" disabled={isLoading} fullWidth>
            {isLoading ? 'Sending Request...' : 'Send Reset Link'}
          </Button>
        </AuthForm>
      )}
    </AuthCard>
  );
};

export default ForgotPasswordView;
