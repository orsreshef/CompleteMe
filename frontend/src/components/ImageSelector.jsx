import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ImageSelector.css';

const CATEGORIES = [
  { id: 'animals',     label: 'Animals',     emoji: '🐾', color: '#10b981' },
  { id: 'space',       label: 'Space',        emoji: '🚀', color: '#6366f1' },
  { id: 'dinosaurs',   label: 'Dinosaurs',    emoji: '🦕', color: '#84cc16' },
  { id: 'ocean',       label: 'Ocean',        emoji: '🐠', color: '#06b6d4' },
  { id: 'flowers',     label: 'Flowers',      emoji: '🌸', color: '#ec4899' },
  { id: 'trains',      label: 'Trains',       emoji: '🚂', color: '#f59e0b' },
  { id: 'butterflies', label: 'Butterflies',  emoji: '🦋', color: '#8b5cf6' },
  { id: 'lions',       label: 'Safari',       emoji: '🦁', color: '#f97316' },
  { id: 'beach',       label: 'Beach',        emoji: '🏖️', color: '#0ea5e9' },
  { id: 'ice cream',   label: 'Ice Cream',    emoji: '🍦', color: '#f472b6' },
  { id: 'rainbow',     label: 'Rainbow',      emoji: '🌈', color: '#a855f7' },
  { id: 'toys',        label: 'Toys',         emoji: '🧸', color: '#ef4444' },
];

const SEARCH_SUGGESTIONS = ['cats', 'robots', 'butterflies', 'trains', 'dolphins', 'mountains'];

const MethodCard = ({ mode, selectedMode, onSelect, emoji, title, description, color }) => (
  <motion.button
    className={`method-card ${selectedMode === mode ? 'active' : ''}`}
    style={{ '--method-color': color }}
    onClick={() => onSelect(mode)}
    whileHover={{ scale: 1.05, y: -4 }}
    whileTap={{ scale: 0.95 }}
  >
    <div className="method-emoji">{emoji}</div>
    <div className="method-title">{title}</div>
    <div className="method-desc">{description}</div>
    {selectedMode === mode && (
      <motion.div
        className="method-checkmark"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        ✓
      </motion.div>
    )}
  </motion.button>
);

const ImageSelector = ({ difficulty, difficultyName, onStartGame, onBack }) => {
  const [selectedMode, setSelectedMode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    setSearchQuery('');
    setSelectedCategory(null);
  };

  const handleStartGame = () => {
    if (selectedMode === 'search') {
      onStartGame({ query: searchQuery.trim() || undefined });
    } else if (selectedMode === 'surprise') {
      onStartGame({});
    } else if (selectedMode === 'category' && selectedCategory) {
      onStartGame({ query: selectedCategory });
    }
  };

  const canStart =
    (selectedMode === 'search' && searchQuery.trim().length > 0) ||
    selectedMode === 'surprise' ||
    (selectedMode === 'category' && selectedCategory !== null);

  return (
    <div className="image-selector-screen">
      <motion.div
        className="image-selector-container"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <motion.div
          className="selector-header"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <motion.button
            className="back-btn"
            onClick={onBack}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            ← Back
          </motion.button>

          <div className="selector-title-wrapper">
            <motion.div
              className="selector-icon"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.2 }}
            >
              🖼️
            </motion.div>
            <h1 className="selector-title">Pick Your Picture!</h1>
            <p className="selector-subtitle">How do you want to find your puzzle image?</p>
          </div>

        </motion.div>

        {/* Method Cards */}
        <motion.div
          className="method-cards"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <MethodCard
            mode="search"
            selectedMode={selectedMode}
            onSelect={handleModeSelect}
            emoji="🔍"
            title="Search"
            description="Type what you love!"
            color="#3b82f6"
          />
          <MethodCard
            mode="surprise"
            selectedMode={selectedMode}
            onSelect={handleModeSelect}
            emoji="🎲"
            title="Surprise Me!"
            description="Mystery picture!"
            color="#f59e0b"
          />
          <MethodCard
            mode="category"
            selectedMode={selectedMode}
            onSelect={handleModeSelect}
            emoji="🐾"
            title="Categories"
            description="Pick a topic!"
            color="#8b5cf6"
          />
        </motion.div>

        {/* Difficulty badge — shown below the 3 option cards */}
        <motion.div
          className="difficulty-badge-row"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <span className="difficulty-badge">{difficultyName} Level</span>
        </motion.div>

        {/* Content Area */}
        <AnimatePresence mode="wait">
          {selectedMode === 'search' && (
            <motion.div
              key="search"
              className="mode-content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.25 }}
            >
              <div className="search-header">
                <span className="mode-content-icon">🔍</span>
                <h3>What should your puzzle show?</h3>
              </div>
              <div className="search-box">
                <input
                  type="text"
                  className="search-input"
                  placeholder="e.g. cats, rockets, forest..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && canStart && handleStartGame()}
                  maxLength={50}
                  autoFocus
                />
              </div>
              <div className="search-suggestions-label">Try one of these:</div>
              <div className="search-suggestions">
                {SEARCH_SUGGESTIONS.map((s) => (
                  <motion.button
                    key={s}
                    className={`suggestion-chip ${searchQuery === s ? 'active' : ''}`}
                    onClick={() => setSearchQuery(s)}
                    whileHover={{ scale: 1.08 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {s}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {selectedMode === 'surprise' && (
            <motion.div
              key="surprise"
              className="mode-content surprise-content"
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.85 }}
              transition={{ duration: 0.25 }}
            >
              <motion.div
                className="surprise-emoji"
                animate={{ rotate: [0, -10, 10, -10, 10, 0] }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                🎁
              </motion.div>
              <h3 className="surprise-title">Mystery Image!</h3>
              <p className="surprise-text">
                We'll pick a completely random surprise picture for you!
              </p>
              <p className="surprise-note">Could be anything... how exciting! 🌟</p>
            </motion.div>
          )}

          {selectedMode === 'category' && (
            <motion.div
              key="category"
              className="mode-content category-content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.25 }}
            >
              <div className="category-header">
                <span className="mode-content-icon">🐾</span>
                <h3>Choose a category!</h3>
              </div>
              <div className="category-grid">
                {CATEGORIES.map((cat, i) => (
                  <motion.button
                    key={cat.id}
                    className={`category-card ${selectedCategory === cat.id ? 'selected' : ''}`}
                    style={{
                      '--cat-color': cat.color,
                      ...(selectedCategory === cat.id
                        ? { borderColor: cat.color, backgroundColor: cat.color + '18' }
                        : {}),
                    }}
                    onClick={() => setSelectedCategory(cat.id)}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.04 }}
                    whileHover={{ scale: 1.08, y: -3 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <span className="cat-emoji">{cat.emoji}</span>
                    <span className="cat-label">{cat.label}</span>
                    {selectedCategory === cat.id && (
                      <motion.span
                        className="cat-checkmark"
                        style={{ background: cat.color }}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 300 }}
                      >
                        ✓
                      </motion.span>
                    )}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Start Button */}
        <AnimatePresence>
          {canStart && (
            <motion.button
              className="start-puzzle-btn"
              onClick={handleStartGame}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.9 }}
              whileHover={{ scale: 1.05, boxShadow: '0 12px 40px rgba(102,126,234,0.5)' }}
              whileTap={{ scale: 0.97 }}
            >
              🧩 Start Puzzle!
            </motion.button>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default ImageSelector;
