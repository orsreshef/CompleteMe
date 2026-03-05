import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import api from '../../services/api';
import './HistoryScreen.css';

const DIFFICULTY_EMOJI = {
  Beginner: '🌟',
  Easy: '⭐',
  Medium: '🔥',
  Hard: '💪',
  Expert: '🚀',
};

const HistoryScreen = ({ user, onBack }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getHistory()
      .then(data => setEntries(data.history))
      .catch(() => setError('Failed to load history.'))
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const totalScore = entries.reduce((sum, e) => sum + (e.score_earned || 0), 0);

  return (
    <div className="history-screen">
      <div className="history-container">
        {/* Header */}
        <motion.div
          className="history-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <button className="btn-back" onClick={onBack}>← Back</button>
          <h1 className="history-title">Game History</h1>
          <div className="history-user">
            <span>{user?.username}</span>
          </div>
        </motion.div>

        {/* Summary stats */}
        {!loading && !error && (
          <motion.div
            className="history-stats"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="stat-card">
              <div className="stat-card-value">{entries.length}</div>
              <div className="stat-card-label">Games Played</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-value">{totalScore}</div>
              <div className="stat-card-label">Total Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-value">
                {entries.length > 0 ? Math.round(totalScore / entries.length) : 0}
              </div>
              <div className="stat-card-label">Avg Score</div>
            </div>
          </motion.div>
        )}

        {/* Content */}
        {loading && (
          <div className="history-loading">
            <div className="spinner"></div>
            <p>Loading your games...</p>
          </div>
        )}

        {error && (
          <div className="history-error">{error}</div>
        )}

        {!loading && !error && entries.length === 0 && (
          <motion.div
            className="history-empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="history-empty-icon">🧩</div>
            <p>No games yet — play your first puzzle!</p>
          </motion.div>
        )}

        {!loading && !error && entries.length > 0 && (
          <motion.div
            className="history-list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {entries.map((entry, i) => (
              <motion.div
                key={entry.game_id}
                className="history-card"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
              >
                {/* Thumbnail */}
                <div className="history-card-thumb">
                  {entry.image_url
                    ? <img src={entry.image_url} alt="Puzzle" />
                    : <span className="history-card-thumb-placeholder">🧩</span>
                  }
                </div>

                {/* Info */}
                <div className="history-card-info">
                  <div className="history-card-top">
                    <span className="history-card-difficulty">
                      {DIFFICULTY_EMOJI[entry.difficulty_level] || '🧩'} {entry.difficulty_level}
                    </span>
                    <span className="history-card-date">{formatDate(entry.played_at)}</span>
                  </div>
                  <div className="history-card-details">
                    <span>{entry.grid_size} pieces</span>
                    <span>·</span>
                    <span>{entry.num_missing_pieces} missing</span>
                  </div>
                </div>

                {/* Score */}
                <div className="history-card-score">
                  +{entry.score_earned}
                  <span className="history-card-score-label">pts</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default HistoryScreen;
