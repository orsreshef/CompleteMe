import React from 'react';
import { motion } from 'framer-motion';
import './LoadingScreen.css';

const LoadingScreen = ({ difficulty }) => {
  const getDifficultyName = (level) => {
    const names = {
      1: 'Beginner',
      2: 'Easy',
      3: 'Medium',
      4: 'Hard',
      5: 'Expert',
    };
    return names[level] || 'Unknown';
  };

  const loadingMessages = [
    '🎨 Selecting a beautiful image...',
    '✂️ Cutting the puzzle pieces...',
    '🤖 Preparing AI validation...',
    '🎯 Creating your challenge...',
    '✨ Almost ready...',
  ];

  const [currentMessage, setCurrentMessage] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % loadingMessages.length);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-screen">
      <div className="loading-container">
        {/* Puzzle pieces animation */}
        <div className="loading-animation">
          <motion.div
            className="puzzle-piece piece-1"
            animate={{
              rotate: [0, 360],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            🧩
          </motion.div>
          <motion.div
            className="puzzle-piece piece-2"
            animate={{
              rotate: [360, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.3,
            }}
          >
            🧩
          </motion.div>
          <motion.div
            className="puzzle-piece piece-3"
            animate={{
              rotate: [0, 360],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: 0.6,
            }}
          >
            🧩
          </motion.div>
        </div>

        {/* Loading text */}
        <motion.h2
          className="loading-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Creating Your Puzzle
        </motion.h2>

        <div className="loading-difficulty">
          Level: <strong>{getDifficultyName(difficulty)}</strong>
        </div>

        {/* Progress messages */}
        <motion.div
          className="loading-message"
          key={currentMessage}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
        >
          {loadingMessages[currentMessage]}
        </motion.div>

        {/* Loading bar */}
        <div className="loading-bar">
          <motion.div
            className="loading-progress"
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{
              duration: 3,
              ease: 'easeInOut',
            }}
          />
        </div>

        {/* Spinner */}
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;
