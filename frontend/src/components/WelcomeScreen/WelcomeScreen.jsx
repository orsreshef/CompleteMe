import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import UserBar from '../UserBar/UserBar';
import './WelcomeScreen.css';

const MAX_REGIONS = { 1: 1, 2: 2, 3: 3, 4: 4, 5: 4 };

const REGION_COLORS = {
  1: '#10b981',
  2: '#3b82f6',
  3: '#f59e0b',
  4: '#8b5cf6',
};

const REGION_EMOJIS = {
  1: '⬛',
  2: '⬛⬛',
  3: '⬛⬛⬛',
  4: '⬛⬛⬛⬛',
};

const AVATARS = { 1: '🦁', 2: '🐼', 3: '🦊', 4: '🐧', 5: '🦋' };

const WelcomeScreen = ({ onStartGame, difficultyLevels, user, onLogout, onHistory, onNewGame, onEditProfile }) => {
  const [selectedDifficulty, setSelectedDifficulty] = useState(null);
  const [selectedRegions, setSelectedRegions] = useState(null);

  const defaultLevels = {
    1: { pieces: 2,  name: 'Beginner' },
    2: { pieces: 4,  name: 'Easy'     },
    3: { pieces: 8,  name: 'Medium'   },
    4: { pieces: 16, name: 'Hard'     },
    5: { pieces: 32, name: 'Expert'   },
  };

  const levels = difficultyLevels || defaultLevels;

  const getDifficultyColor = (level) => {
    const colors = { 1: '#10b981', 2: '#3b82f6', 3: '#f59e0b', 4: '#ef4444', 5: '#8b5cf6' };
    return colors[level] || '#6366f1';
  };

  const getDifficultyEmoji = (level) => {
    const emojis = { 1: '🌟', 2: '⭐', 3: '🔥', 4: '💪', 5: '🚀' };
    return emojis[level] || '🧩';
  };

  const handleDifficultyClick = (level) => {
    setSelectedDifficulty(level);
    setSelectedRegions(null);
  };

  const handleContinue = () => {
    if (selectedDifficulty && selectedRegions) {
      onStartGame(selectedDifficulty, selectedRegions);
    }
  };

  const maxRegions = selectedDifficulty ? MAX_REGIONS[selectedDifficulty] : 0;

  return (
    <div className="welcome-screen">
      <UserBar user={user} onLogout={onLogout} onHistory={onHistory} onNewGame={onNewGame} onEditProfile={onEditProfile} />

      <motion.div
        className="welcome-container"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <motion.div
          className="welcome-header"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.2 }}
        >
          <div className="puzzle-icon">🧩</div>
          <h1 className="welcome-title">Complete Me</h1>
          <p className="welcome-subtitle">Interactive Educational Puzzles utilizing CV &amp; Deep Learning</p>
        </motion.div>

        {/* Step 1 — Difficulty */}
        <motion.div
          className="difficulty-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="difficulty-title">Step 1 — Choose Your Level</h2>

          <div className="difficulty-grid">
            {Object.entries(levels).map(([level, info], index) => {
              const lvl = Number.parseInt(level, 10);
              const isSelected = selectedDifficulty === lvl;
              return (
                <motion.button
                  key={level}
                  className={`difficulty-card ${isSelected ? 'selected' : ''}`}
                  style={{ '--card-color': getDifficultyColor(lvl) }}
                  onClick={() => handleDifficultyClick(lvl)}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(0,0,0,0.15)' }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="difficulty-emoji">{getDifficultyEmoji(lvl)}</div>
                  <div className="difficulty-name">{info.name}</div>
                  <div className="difficulty-pieces">{info.pieces} pieces</div>
                  {isSelected && (
                    <motion.div
                      className="difficulty-selected-badge"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 300 }}
                    >
                      ✓
                    </motion.div>
                  )}
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Step 2 — Region count */}
        <AnimatePresence>
          {selectedDifficulty && (
            <motion.div
              className="region-section"
              initial={{ opacity: 0, y: -20, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -20, height: 0 }}
              transition={{ duration: 0.35 }}
            >
              <h2 className="difficulty-title">Step 2 — How many missing pieces?</h2>

              <div className="region-grid">
                {Array.from({ length: maxRegions }, (_, i) => i + 1).map((count, index) => {
                  const isSelected = selectedRegions === count;
                  return (
                    <motion.button
                      key={count}
                      className={`region-card ${isSelected ? 'selected' : ''}`}
                      style={{ '--region-color': REGION_COLORS[count] }}
                      onClick={() => setSelectedRegions(count)}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.08 }}
                      whileHover={{ scale: 1.06, y: -3 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <div className="region-emoji">{REGION_EMOJIS[count]}</div>
                      <div className="region-count">{count}</div>
                      <div className="region-label">
                        {count === 1 ? 'missing piece' : 'missing pieces'}
                      </div>
                      {isSelected && (
                        <motion.div
                          className="region-selected-badge"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: 'spring', stiffness: 300 }}
                        >
                          ✓
                        </motion.div>
                      )}
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Continue button */}
        <AnimatePresence>
          {selectedDifficulty && selectedRegions && (
            <motion.button
              className="btn-continue"
              onClick={handleContinue}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20 }}
              whileHover={{ scale: 1.05, boxShadow: '0 12px 40px rgba(0,0,0,0.25)' }}
              whileTap={{ scale: 0.97 }}
            >
              Let's Play! →
            </motion.button>
          )}
        </AnimatePresence>

        {/* Features */}
        <motion.div
          className="features-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <span className="feature-text">Computer Vision Validation</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🖥️</span>
            <span className="feature-text">Deep Learning Validation</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎨</span>
            <span className="feature-text">Beautiful Images</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🧠</span>
            <span className="feature-text">Educational &amp; Fun</span>
          </div>
        </motion.div>

        <motion.div
          className="welcome-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <p>Computer Science Final Year Project</p>
        </motion.div>
      </motion.div>
    </div>
  );
};

WelcomeScreen.propTypes = {
  onStartGame:      PropTypes.func.isRequired,
  difficultyLevels: PropTypes.object,
  user:             PropTypes.object,
  onLogout:         PropTypes.func,
  onHistory:        PropTypes.func,
  onNewGame:        PropTypes.func,
  onEditProfile:    PropTypes.func,
};

WelcomeScreen.defaultProps = {
  difficultyLevels: null,
  user:             null,
  onLogout:         () => {},
  onHistory:        () => {},
  onNewGame:        () => {},
  onEditProfile:    () => {},
};

export default WelcomeScreen;
