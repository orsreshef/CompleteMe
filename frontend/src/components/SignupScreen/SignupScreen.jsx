import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import './SignupScreen.css';
import api from '../../services/api';

// Placeholder avatars — will be replaced with real images in a future update
const AVATARS = [
  { id: 1, emoji: '🦁', label: 'Lion' },
  { id: 2, emoji: '🐼', label: 'Panda' },
  { id: 3, emoji: '🦊', label: 'Fox' },
  { id: 4, emoji: '🐧', label: 'Penguin' },
  { id: 5, emoji: '🦋', label: 'Butterfly' },
];

const SignupScreen = ({ onLogin, onGoLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [avatarId, setAvatarId] = useState(1);
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
      const data = await api.register(username.trim(), email.trim(), password, avatarId);
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
      {/* Left branding panel */}
      <motion.div
        className="auth-panel-left"
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="auth-brand-logo">🧩</div>
        <h1 className="auth-brand-name">Complete Me</h1>
        <p className="auth-brand-tagline">
          Interactive Educational Puzzles utilizing Computer Vision &amp; Deep Learning
        </p>
        <div className="auth-brand-features">
          <div className="auth-brand-feature">
            <span>🤖</span>
            <span>CV-powered validation</span>
          </div>
          <div className="auth-brand-feature">
            <span>🧠</span>
            <span>Deep Learning analysis</span>
          </div>
          <div className="auth-brand-feature">
            <span>🎨</span>
            <span>Beautiful real-world images</span>
          </div>
          <div className="auth-brand-feature">
            <span>📊</span>
            <span>Track your progress</span>
          </div>
        </div>
      </motion.div>

      {/* Right form panel */}
      <div className="auth-panel-right">
        <motion.div
          className="auth-card"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
        >
          <button className="btn-back" onClick={onGoLogin}>
            ← Back to Sign In
          </button>
          <h2 className="auth-title">Create your account</h2>
          <p className="auth-subtitle">Join Complete Me and start solving puzzles</p>

          {/* Avatar picker */}
          <div className="avatar-section">
            <p className="avatar-label">Choose your avatar</p>
            <div className="avatar-grid">
              {AVATARS.map((av) => (
                <motion.button
                  key={av.id}
                  type="button"
                  className={`avatar-option ${avatarId === av.id ? 'avatar-selected' : ''}`}
                  onClick={() => setAvatarId(av.id)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  title={av.label}
                  disabled={isLoading}
                >
                  <span className="avatar-emoji">{av.emoji}</span>
                  {avatarId === av.id && (
                    <motion.div
                      className="avatar-check"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 400 }}
                    >
                      ✓
                    </motion.div>
                  )}
                </motion.button>
              ))}
            </div>
          </div>

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <div className="form-row">
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
            </div>

            <div className="form-row">
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
            </div>

            <motion.button
              type="submit"
              className="btn-auth-primary"
              disabled={isLoading}
              whileHover={isLoading ? {} : { scale: 1.02 }}
              whileTap={isLoading ? {} : { scale: 0.98 }}
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
    </div>
  );
};

export default SignupScreen;
