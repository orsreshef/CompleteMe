import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import './LoginScreen.css';
import api from '../../services/api';

const LoginScreen = ({ onLogin, onGuest, onGoSignup }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email.trim() || !password) {
      toast.warning('Please enter your email and password.');
      return;
    }

    setIsLoading(true);
    try {
      const data = await api.login(email.trim(), password);
      toast.success(`Welcome back, ${data.user.username}!`);
      onLogin(data.user);
    } catch (err) {
      toast.error(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <motion.div
        className="auth-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="auth-logo">🧩</div>
        <h1 className="auth-title">AI Puzzle Game</h1>
        <p className="auth-subtitle">Sign in to save your progress</p>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              autoComplete="current-password"
            />
          </div>

          <motion.button
            type="submit"
            className="btn-auth-primary"
            disabled={isLoading}
            whileHover={!isLoading ? { scale: 1.02 } : {}}
            whileTap={!isLoading ? { scale: 0.98 } : {}}
          >
            {isLoading ? <span className="spinner-small" /> : 'Sign In'}
          </motion.button>
        </form>

        <div className="auth-divider"><span>or</span></div>

        <motion.button
          className="btn-auth-guest"
          onClick={onGuest}
          disabled={isLoading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Play as Guest
        </motion.button>

        <p className="auth-switch">
          Don't have an account?{' '}
          <button className="link-btn" onClick={onGoSignup}>
            Sign up
          </button>
        </p>
      </motion.div>
    </div>
  );
};

export default LoginScreen;
