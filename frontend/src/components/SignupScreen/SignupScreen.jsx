import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import './SignupScreen.css';
import api from '../../services/api';

const SignupScreen = ({ onLogin, onGoLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    if (!username.trim() || !email.trim() || !password || !confirm) {
      toast.warning('Please fill in all fields.');
      return false;
    }
    if (username.trim().length < 3) {
      toast.warning('Username must be at least 3 characters.');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      toast.warning('Please enter a valid email address.');
      return false;
    }
    if (password.length < 6) {
      toast.warning('Password must be at least 6 characters.');
      return false;
    }
    if (password !== confirm) {
      toast.warning('Passwords do not match.');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    try {
      const data = await api.register(username.trim(), email.trim(), password);
      toast.success(`Welcome, ${data.user.username}! Account created.`);
      onLogin(data.user);
    } catch (err) {
      toast.error(err.message || 'Registration failed. Please try again.');
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
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join and track your puzzle progress</p>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="signup-username">Username</label>
            <input
              id="signup-username"
              type="text"
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="signup-email">Email</label>
            <input
              id="signup-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="signup-password">Password</label>
            <input
              id="signup-password"
              type="password"
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="signup-confirm">Confirm Password</label>
            <input
              id="signup-confirm"
              type="password"
              placeholder="Repeat your password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              disabled={isLoading}
              autoComplete="new-password"
            />
          </div>

          <motion.button
            type="submit"
            className="btn-auth-primary"
            disabled={isLoading}
            whileHover={!isLoading ? { scale: 1.02 } : {}}
            whileTap={!isLoading ? { scale: 0.98 } : {}}
          >
            {isLoading ? <span className="spinner-small" /> : 'Create Account'}
          </motion.button>
        </form>

        <p className="auth-switch">
          Already have an account?{' '}
          <button className="link-btn" onClick={onGoLogin}>
            Sign in
          </button>
        </p>
      </motion.div>
    </div>
  );
};

export default SignupScreen;
