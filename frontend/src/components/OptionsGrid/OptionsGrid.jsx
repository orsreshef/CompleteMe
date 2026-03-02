import React from 'react';
import { motion } from 'framer-motion';
import './OptionsGrid.css';

const OptionsGrid = ({ options, selectedOption, onSelect, disabled }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="options-section">
      <h3 className="options-title">Choose the correct piece:</h3>

      <motion.div
        className="options-grid"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {options.map((option, index) => (
          <motion.div
            key={index}
            variants={itemVariants}
            className={`option-card ${selectedOption === index ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onSelect(index)}
            whileHover={!disabled ? { scale: 1.05 } : {}}
            whileTap={!disabled ? { scale: 0.95 } : {}}
          >
            <div className="option-number">{index + 1}</div>
            <div className="option-image-wrapper">
              <img
                src={option}
                alt={`Option ${index + 1}`}
                className="option-image"
              />
            </div>
            {selectedOption === index && (
              <motion.div
                className="selection-indicator"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              >
                ✓
              </motion.div>
            )}
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default OptionsGrid;