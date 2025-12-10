import React from 'react';
import { motion } from 'framer-motion';
import './PuzzleImage.css';

const PuzzleImage = ({ puzzleImage, difficulty }) => {
  return (
    <motion.div
      className="puzzle-image-container"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="puzzle-card">
        <div className="puzzle-header">
          <span className="puzzle-label">🎯 Find the missing piece:</span>
          <span className="puzzle-difficulty">
            {difficulty.pieces} pieces puzzle
          </span>
        </div>

        <div className="puzzle-image-wrapper">
          <img
            src={puzzleImage}
            alt="Puzzle with missing piece"
            className="puzzle-image"
          />
          
          {/* Decorative border */}
          <div className="puzzle-border"></div>
        </div>

        <div className="puzzle-hint-text">
          <span className="hint-icon">💡</span>
          Look carefully at the colors and patterns around the black square
        </div>
      </div>
    </motion.div>
  );
};

export default PuzzleImage;