import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import './GameBoard.css';

import ValidationModal from '../ValidationModal/ValidationModal';
import api from '../../services/api';

const GameBoard = ({ gameData, difficulty, onRestart, onComplete }) => {
  // placements: { zoneIndex (string) -> optionIndex (number) }
  const [placements, setPlacements] = useState({});
  const [draggedPiece, setDraggedPiece] = useState(null);
  const [hoveredZone, setHoveredZone] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [attempts, setAttempts] = useState(0);

  const {
    puzzle_image,
    options,
    missing_positions,
    image_dimensions,
    num_regions,
    difficulty: diffInfo,
  } = gameData;

  const placedOptionIndices = new Set(Object.values(placements));
  const pieceAspectRatio = `${missing_positions[0].width} / ${missing_positions[0].height}`;
  const allZonesFilled = Object.keys(placements).length === num_regions;

  const emptyZones = missing_positions
    .map((_, i) => i)
    .filter((i) => !placements.hasOwnProperty(i));
  const hintEnabled = emptyZones.length === 1;

  // ── Drag handlers ────────────────────────────────────────────────────
  const handleDragStart = (e, optionIndex) => {
    setDraggedPiece(optionIndex);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragEnd = () => {
    setDraggedPiece(null);
    setHoveredZone(null);
  };

  const handleZoneDragOver = (e, zoneIndex) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setHoveredZone(zoneIndex);
  };

  const handleZoneDragLeave = (e) => {
    // Only clear if leaving the zone itself (not a child element)
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setHoveredZone(null);
    }
  };

  const handleZoneDrop = (e, zoneIndex) => {
    e.preventDefault();
    if (draggedPiece === null) return;

    setPlacements((prev) => {
      // Remove draggedPiece from any zone it was already in
      const next = Object.fromEntries(Object.entries(prev).filter(([, v]) => v !== draggedPiece));
      next[zoneIndex] = draggedPiece;
      return next;
    });

    setDraggedPiece(null);
    setHoveredZone(null);
  };

  const handleZoneClick = (zoneIndex) => {
    if (!placements.hasOwnProperty(zoneIndex)) return;
    setPlacements((prev) => {
      const next = { ...prev };
      delete next[zoneIndex];
      return next;
    });
  };

  // ── Submit ─────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    if (!allZonesFilled) {
      toast.warning('Place a piece in every black square first!');
      return;
    }

    setIsValidating(true);
    setAttempts((prev) => prev + 1);

    try {
      const placementsArray = Object.entries(placements).map(([zoneIndex, optionIndex]) => ({
        zone_index: parseInt(zoneIndex),
        option_index: parseInt(optionIndex),
      }));

      const result = await api.validateAnswer(gameData.game_id, placementsArray);
      console.log('Validation result:', result);

      setValidationResult(result);
      setShowModal(true);

      if (result.is_correct) {
        setTimeout(() => onComplete(result.score_earned ?? 0), 1500);
      }
    } catch (error) {
      console.error('Validation error:', error);
      toast.error('Validation failed. Please try again.');
    } finally {
      setIsValidating(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    if (!validationResult?.is_correct && validationResult?.region_results) {
      // Remove placements for zones that were wrong
      const wrongZones = validationResult.region_results
        .filter((r) => !r.is_correct)
        .map((r) => String(r.zone_index));
      if (wrongZones.length > 0) {
        setPlacements((prev) => {
          const next = { ...prev };
          wrongZones.forEach((z) => delete next[z]);
          return next;
        });
      }
    }
  };

  const handleHint = async () => {
    try {
      const hint = await api.getHint(gameData.game_id, emptyZones[0]);
      toast.info(hint.hint, { position: 'top-center', autoClose: 5000 });
    } catch (error) {
      toast.error('Failed to get hint');
    }
  };

  // ── Zone positioning (percentage-based) ────────────────────────────
  const zonePct = (pos) => {
    const { width: imgW, height: imgH } = image_dimensions;
    return {
      left: `${(pos.x / imgW) * 100}%`,
      top: `${(pos.y / imgH) * 100}%`,
      width: `${(pos.width / imgW) * 100}%`,
      height: `${(pos.height / imgH) * 100}%`,
    };
  };

  return (
    <div className="game-board">
      <div className="game-container">
        {/* Header */}
        <motion.div
          className="game-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="game-info">
            <h2 className="game-title">
              {num_regions === 1
                ? 'Find the Missing Piece! 🧩'
                : `Fill ${num_regions} Missing Pieces! 🧩`}
            </h2>
            <div className="game-stats">
              <span className="stat-item">
                <span className="stat-label">Level:</span>
                <span className="stat-value">{diffInfo?.name}</span>
              </span>
              <span className="stat-item">
                <span className="stat-label">Filled:</span>
                <span className="stat-value">
                  {Object.keys(placements).length}/{num_regions}
                </span>
              </span>
              <span className="stat-item">
                <span className="stat-label">Attempts:</span>
                <span className="stat-value">{attempts}</span>
              </span>
            </div>
          </div>

          <div className="game-actions">
            <button
              className={`btn-hint ${!hintEnabled ? 'btn-hint--disabled' : ''}`}
              onClick={handleHint}
              disabled={!hintEnabled || isValidating}
              title={
                !hintEnabled
                  ? `Fill ${emptyZones.length - 1} more piece${emptyZones.length - 1 !== 1 ? 's' : ''} to unlock the hint`
                  : 'Get a hint for the last piece'
              }
            >
              💡 Hint
            </button>
            <button className="btn-restart" onClick={onRestart} disabled={isValidating}>
              🔄 New Game
            </button>
          </div>
        </motion.div>

        {/* Instruction */}
        <motion.p
          className="puzzle-instruction"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Drag pieces from below onto the black squares. Click a placed piece to remove it.
        </motion.p>

        {/* Puzzle image with drop zones */}
        <motion.div
          className="puzzle-wrapper-container"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.25 }}
        >
          <div className="puzzle-wrapper">
            <img className="puzzle-img" src={puzzle_image} alt="Puzzle" draggable={false} />

            {missing_positions.map((pos, zoneIndex) => {
              const isFilled = placements.hasOwnProperty(zoneIndex);
              const isHovered = hoveredZone === zoneIndex;
              return (
                <div
                  key={zoneIndex}
                  className={`drop-zone ${isFilled ? 'zone-filled' : 'zone-empty'} ${isHovered ? 'zone-hovered' : ''}`}
                  style={zonePct(pos)}
                  onDragOver={(e) => handleZoneDragOver(e, zoneIndex)}
                  onDragLeave={handleZoneDragLeave}
                  onDrop={(e) => handleZoneDrop(e, zoneIndex)}
                  onClick={() => handleZoneClick(zoneIndex)}
                >
                  {isFilled ? (
                    <>
                      <img
                        className="placed-piece-img"
                        src={options[placements[zoneIndex]]}
                        alt={`Piece in zone ${zoneIndex + 1}`}
                        draggable={false}
                      />
                      <div className="zone-remove-hint">✕</div>
                    </>
                  ) : (
                    <div className="zone-empty-label">{zoneIndex + 1}</div>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Piece pool */}
        <motion.div
          className="piece-pool"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="pool-title">Drag a piece onto a black square:</div>
          <div className="pool-grid">
            {options.map((optionBase64, idx) => {
              const isPlaced = placedOptionIndices.has(idx);
              const isDragging = draggedPiece === idx;
              return (
                <div
                  key={idx}
                  className={`pool-piece ${isPlaced ? 'pool-piece-placed' : ''} ${isDragging ? 'pool-piece-dragging' : ''}`}
                  style={{ aspectRatio: pieceAspectRatio }}
                  draggable={!isPlaced && !isValidating}
                  onDragStart={(e) => !isPlaced && handleDragStart(e, idx)}
                  onDragEnd={handleDragEnd}
                >
                  <img src={optionBase64} alt={`Option ${idx + 1}`} draggable={false} />
                  {isPlaced && <div className="piece-placed-overlay">✓</div>}
                  {!isPlaced && <div className="piece-number">{idx + 1}</div>}
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Submit */}
        <motion.div
          className="submit-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <button
            className={`btn-submit ${allZonesFilled ? 'active' : ''}`}
            onClick={handleSubmit}
            disabled={!allZonesFilled || isValidating}
          >
            {isValidating ? (
              <>
                <span className="spinner-small"></span>
                Checking with AI...
              </>
            ) : (
              <>✓ Check Answer{num_regions > 1 ? 's' : ''}</>
            )}
          </button>
        </motion.div>
      </div>

      {showModal && validationResult && (
        <ValidationModal result={validationResult} onClose={handleCloseModal} />
      )}
    </div>
  );
};

export default GameBoard;
