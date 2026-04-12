import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ValidationModal.css';

const getConfidenceColor = (score) => {
  if (score >= 0.85) return '#10b981';
  if (score >= 0.7) return '#3b82f6';
  if (score >= 0.5) return '#f59e0b';
  return '#ef4444';
};

const getConfidenceLabel = (score) => {
  if (score >= 0.85) return 'Excellent';
  if (score >= 0.7) return 'Good';
  if (score >= 0.5) return 'Moderate';
  return 'Low';
};

const ConfidenceBar = ({ confidence, label }) => (
  <div className="confidence-section">
    <div className="confidence-label">
      {label || 'AI Confidence'}: {(confidence * 100).toFixed(1)}%
    </div>
    <div className="confidence-bar">
      <motion.div
        className="confidence-fill"
        style={{ background: getConfidenceColor(confidence) }}
        initial={{ width: 0 }}
        animate={{ width: `${confidence * 100}%` }}
        transition={{ duration: 0.9, delay: 0.3 }}
      />
    </div>
    <div className="confidence-rating">{getConfidenceLabel(confidence)} Match</div>
  </div>
);

const ValidationModal = ({ result, onClose }) => {
  const { is_correct, confidence, validation_details, region_results } = result;
  const isMultiRegion = Array.isArray(region_results) && region_results.length > 1;

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.8, y: 50 },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { type: 'spring', stiffness: 300, damping: 30 },
    },
    exit: { opacity: 0, scale: 0.8, y: 50 },
  };

  return (
    <AnimatePresence>
      <motion.div
        className="modal-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className={`validation-modal ${is_correct ? 'correct' : 'incorrect'}`}
          variants={modalVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Icon */}
          <motion.div
            className="modal-icon"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
          >
            {is_correct ? '🎉' : '❌'}
          </motion.div>

          {/* Title */}
          <h2 className="modal-title">{is_correct ? 'Correct!' : 'Not Quite Right'}</h2>

          {/* Message */}
          <p className="modal-message">
            {is_correct
              ? isMultiRegion
                ? 'Amazing! All pieces are in the right place!'
                : 'Amazing work! You found the correct piece!'
              : isMultiRegion
                ? 'Some pieces are wrong. Try again!'
                : "That's not the right piece. Try again!"}
          </p>

          {/* Multi-region: per-zone results */}
          {isMultiRegion && (
            <div className="region-results">
              <h4 className="details-title">Zone Results:</h4>
              <div className="region-results-grid">
                {region_results.map((r) => (
                  <div
                    key={r.zone_index}
                    className={`region-result-item ${r.is_correct ? 'match' : 'no-match'}`}
                  >
                    <span className="region-result-icon">{r.is_correct ? '✓' : '✗'}</span>
                    <span className="region-result-label">Zone {r.zone_index + 1}</span>
                    <span className="region-result-pct">{(r.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>

              {/* Overall bar */}
              <ConfidenceBar confidence={confidence} label="Overall Confidence" />
            </div>
          )}

          {/* Single-region: confidence bar + details */}
          {!isMultiRegion && (
            <>
              <ConfidenceBar confidence={confidence} />

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
            </>
          )}

          {/* Close button */}
          <button className="modal-close-btn" onClick={onClose}>
            {is_correct ? 'Continue' : 'Try Again'}
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ValidationModal;
