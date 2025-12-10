import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Confetti from 'react-confetti';
import { toast } from 'react-toastify';
import './GameBoard.css';

import PuzzleImage from './PuzzleImage';
import OptionsGrid from './OptionsGrid';
import ValidationModal from './ValidationModal';
import api from '../services/api';

const GameBoard = ({ gameData, difficulty, onRestart, onComplete }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  const handleOptionSelect = (index) => {
    if (isValidating || showModal) return;
    
    setSelectedOption(index);
    console.log(`Selected option: ${index}`);
  };

  const handleSubmit = async () => {
    if (selectedOption === null) {
      toast.warning('Please select a piece first!');
      return;
    }

    setIsValidating(true);
    setAttempts(prev => prev + 1);

    try {
      console.log('🔍 Validating answer...');
      
      // Get the selected piece image
      const selectedPieceImage = gameData.options[selectedOption];

      const result = await api.validateAnswer(
        gameData.game_id,
        selectedOption,
        selectedPieceImage
      );

      console.log('✅ Validation result:', result);

      setValidationResult(result);
      setShowModal(true);

      if (result.is_correct) {
        setShowConfetti(true);
        
        // Auto-complete after showing modal
        setTimeout(() => {
          onComplete();
        }, 3000);
      }

    } catch (error) {
      console.error('❌ Validation error:', error);
      toast.error('Validation failed. Please try again.');
    } finally {
      setIsValidating(false);
    }
  };

  const handleHint = async () => {
    try {
      const hint = await api.getHint(gameData.game_id);
      toast.info(hint.hint, {
        position: 'top-center',
        autoClose: 5000
      });
    } catch (error) {
      console.error('❌ Hint error:', error);
      toast.error('Failed to get hint');
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    if (!validationResult?.is_correct) {
      setSelectedOption(null);
    }
  };

  return (
    <div className="game-board">
      {showConfetti && (
        <Confetti
          width={window.innerWidth}
          height={window.innerHeight}
          recycle={false}
          numberOfPieces={500}
        />
      )}

      <div className="game-container">
        {/* Header */}
        <motion.div
          className="game-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="game-info">
            <h2 className="game-title">Find the Missing Piece! 🧩</h2>
            <div className="game-stats">
              <span className="stat-item">
                <span className="stat-label">Level:</span>
                <span className="stat-value">{gameData.difficulty.name}</span>
              </span>
              <span className="stat-item">
                <span className="stat-label">Attempts:</span>
                <span className="stat-value">{attempts}</span>
              </span>
            </div>
          </div>

          <div className="game-actions">
            <button 
              className="btn-hint"
              onClick={handleHint}
              disabled={isValidating}
            >
              💡 Hint
            </button>
            <button 
              className="btn-restart"
              onClick={onRestart}
              disabled={isValidating}
            >
              🔄 New Game
            </button>
          </div>
        </motion.div>

        {/* Puzzle Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <PuzzleImage
            puzzleImage={gameData.puzzle_image}
            difficulty={gameData.difficulty}
          />
        </motion.div>

        {/* Options Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <OptionsGrid
            options={gameData.options}
            selectedOption={selectedOption}
            onSelect={handleOptionSelect}
            disabled={isValidating || showModal}
          />
        </motion.div>

        {/* Submit Button */}
        <motion.div
          className="submit-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <button
            className={`btn-submit ${selectedOption !== null ? 'active' : ''}`}
            onClick={handleSubmit}
            disabled={selectedOption === null || isValidating}
          >
            {isValidating ? (
              <>
                <span className="spinner-small"></span>
                Checking with AI...
              </>
            ) : (
              <>
                ✓ Check Answer
              </>
            )}
          </button>
        </motion.div>
      </div>

      {/* Validation Modal */}
      {showModal && validationResult && (
        <ValidationModal
          result={validationResult}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default GameBoard;