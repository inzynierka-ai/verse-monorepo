import { useState, useEffect } from 'react';

/**
 * Hook for handling authentication state
 * @returns Object containing authentication state and methods
 */
export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check for authentication token in localStorage
    const token = localStorage.getItem('authToken');
    setIsLoggedIn(!!token);
  }, []);

  const login = (token: string) => {
    localStorage.setItem('authToken', token);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setIsLoggedIn(false);
  };

  return {
    isLoggedIn,
    login,
    logout
  };
};

export default useAuth; 