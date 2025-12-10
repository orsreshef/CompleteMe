import React from 'react';
import { motion } from 'framer-motion';
import './WelcomeScreen.css';

const WelcomeScreen = ({ onStartGame, difficultyLevels }) => {
  const defaultLevels = {
    1: { pieces: 2, name: 'Beginner' },
    2: { pieces: 4, name: 'Easy' },
    3: { pieces: 8, name: 'Medium' },
    4: { pieces: 16, name: 'Hard' },
    5: { pieces: 32, name: 'Expert' }
  };

  const levels = difficultyLevels || defaultLevels;

  const getDifficultyColor = (level) => {
    const colors = {
      1: '#10b981',  // green
      2: '#3b82f6',  // blue
      3: '#f59e0b',  // orange
      4: '#ef4444',  // red
      5: '#8b5cf6'   // purple
    };
    return colors[level] || '#6366f1';
  };

  const getDifficultyEmoji = (level) => {
    const emojis = {
      1: '🌟',
      2: '⭐',
      3: '🔥',
      4: '💪',
      5: '🚀'
    };
    return emojis[level] || '🧩';
  };

  return (
    <div className="welcome-screen">
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
          transition={{ 
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.2
          }}
        >
          <div className="puzzle-icon">🧩</div>
          <h1 className="welcome-title">AI Puzzle Game</h1>
          <p className="welcome-subtitle">
            Find the missing piece using your observation skills!
          </p>
        </motion.div>

        {/* Difficulty Selection */}
        <motion.div
          className="difficulty-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="difficulty-title">Choose Your Level</h2>
          
          <div className="difficulty-grid">
            {Object.entries(levels).map(([level, info], index) => (
              <motion.button
                key={level}
                className="difficulty-card"
                style={{ 
                  '--card-color': getDifficultyColor(parseInt(level))
                }}
                onClick={() => onStartGame(parseInt(level))}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15)'
                }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="difficulty-emoji">
                  {getDifficultyEmoji(parseInt(level))}
                </div>
                <div className="difficulty-name">{info.name}</div>
                <div className="difficulty-pieces">{info.pieces} pieces</div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          className="features-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <span className="feature-text">AI-Powered Validation</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎨</span>
            <span className="feature-text">Beautiful Images</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🧠</span>
            <span className="feature-text">Educational & Fun</span>
          </div>
        </motion.div>

        {/* Footer */}
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

export default WelcomeScreen;