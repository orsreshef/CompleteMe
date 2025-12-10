import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ValidationModal.css';

const ValidationModal = ({ result, onClose }) => {
  const { is_correct, confidence, validation_details } = result;

  const getConfidenceColor = (score) => {
    if (score >= 0.85) return '#10b981'; // green
    if (score >= 0.70) return '#3b82f6'; // blue
    if (score >= 0.50) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const getConfidenceLabel = (score) => {
    if (score >= 0.85) return 'Excellent';
    if (score >= 0.70) return 'Good';
    if (score >= 0.50) return 'Moderate';
    return 'Low';
  };

  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  };

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.8, y: 50 },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.8, 
      y: 50 
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        className="modal-backdrop"
        variants={backdropVariants}
        initial="hidden"
        animate="visible"
        exit="hidden"
        onClick={onClose}
      >
        <motion.div
          className={`validation-modal ${is_correct ? 'correct' : 'incorrect'}`}
          variants={modalVariants}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Icon */}
          <motion.div
            className="modal-icon"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              type: "spring",
              stiffness: 200,
              delay: 0.2 
            }}
          >
            {is_correct ? '🎉' : '❌'}
          </motion.div>

          {/* Title */}
          <h2 className="modal-title">
            {is_correct ? 'Correct!' : 'Not Quite Right'}
          </h2>

          {/* Message */}
          <p className="modal-message">
            {is_correct 
              ? 'Amazing work! You found the correct piece!'
              : 'That\'s not the right piece. Try again!'}
          </p>

          {/* Confidence Score */}
          <div className="confidence-section">
            <div className="confidence-label">
              AI Confidence: {(confidence * 100).toFixed(1)}%
            </div>
            <div className="confidence-bar">
              <motion.div
                className="confidence-fill"
                style={{ 
                  background: getConfidenceColor(confidence)
                }}
                initial={{ width: 0 }}
                animate={{ width: `${confidence * 100}%` }}
                transition={{ duration: 1, delay: 0.3 }}
              />
            </div>
            <div className="confidence-rating">
              {getConfidenceLabel(confidence)} Match
            </div>
          </div>

          {/* Validation Details */}
          {validation_details && (
            <div className="validation-details">
              <h4 className="details-title">AI Analysis:</h4>
              <div className="details-grid">
                {validation_details.features_score !== undefined && (
                  <div className="detail-item">
                    <span className="detail-label">🧠 Features:</span>
                    <span className="detail-value">
                      {(validation_details.features_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                {validation_details.color_score !== undefined && (
                  <div className="detail-item">
                    <span className="detail-label">🎨 Colors:</span>
                    <span className="detail-value">
                      {(validation_details.color_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                {validation_details.texture_score !== undefined && (
                  <div className="detail-item">
                    <span className="detail-label">🔲 Texture:</span>
                    <span className="detail-value">
                      {(validation_details.texture_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                {validation_details.edge_score !== undefined && (
                  <div className="detail-item">
                    <span className="detail-label">📐 Edges:</span>
                    <span className="detail-value">
                      {(validation_details.edge_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                {validation_details.semantic_score !== undefined && (
                  <div className="detail-item">
                    <span className="detail-label">🤖 Semantic:</span>
                    <span className="detail-value">
                      {(validation_details.semantic_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Close Button */}
          <button
            className="modal-close-btn"
            onClick={onClose}
          >
            {is_correct ? 'Continue' : 'Try Again'}
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ValidationModal;