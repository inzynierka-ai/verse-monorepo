import { useState, FormEvent } from 'react';
import { Link } from '@tanstack/react-router';
import styles from '../styles/auth.module.scss';
import { useForgotPassword, ForgotPasswordRequest } from '../../../services/api';

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

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <div className={styles.logoContainer}>
          <h1>VERSE</h1>
        </div>

        <h2 className={styles.title}>Reset Password</h2>
        <p className={styles.subtitle}>
          {isSubmitted
            ? 'Check your email for password reset instructions'
            : 'Enter your email to receive password reset instructions'}
        </p>

        {requestError && <div className={styles.error}>{requestError}</div>}

        {isSubmitted ? (
          <div className={styles.successMessage}>
            Password reset instructions have been sent to your email. Please check your inbox and
            follow the instructions to reset your password.
          </div>
        ) : (
          <form className={styles.form} onSubmit={handleSubmit}>
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

            <button type="submit" className={styles.button} disabled={isLoading}>
              {isLoading ? 'Sending Request...' : 'Send Reset Link'}
            </button>
          </form>
        )}

        <div className={styles.linkContainer}>
          Remember your password?
          <Link to="/login" className={styles.link}>
            Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordView;
