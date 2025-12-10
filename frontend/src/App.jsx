import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import WelcomeScreen from './components/WelcomeScreen';
import GameBoard from './components/GameBoard';
import LoadingScreen from './components/LoadingScreen';
import api from './services/api';

function App() {
  const [gameState, setGameState] = useState('welcome'); // 'welcome', 'loading', 'playing', 'finished'
  const [difficulty, setDifficulty] = useState(1);
  const [gameData, setGameData] = useState(null);
  const [config, setConfig] = useState(null);

  useEffect(() => {
    // Load configuration on mount
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const configData = await api.getConfig();
      setConfig(configData);
      console.log('✅ Configuration loaded:', configData);
    } catch (error) {
      console.error('❌ Failed to load configuration:', error);
      toast.error('Failed to load game configuration');
    }
  };

  const startGame = async (selectedDifficulty) => {
    setDifficulty(selectedDifficulty);
    setGameState('loading');

    try {
      console.log(`🎮 Starting game with difficulty ${selectedDifficulty}...`);
      
      const data = await api.createPuzzle({
        difficulty: selectedDifficulty,
        use_random_image: true
      });

      console.log('✅ Puzzle created:', data);

      setGameData(data);
      setGameState('playing');

      toast.success('Puzzle created! Find the missing piece! 🧩', {
        position: 'top-center',
        autoClose: 3000
      });

    } catch (error) {
      console.error('❌ Failed to create puzzle:', error);
      toast.error('Failed to create puzzle. Please try again.');
      setGameState('welcome');
    }
  };

  const restartGame = () => {
    setGameState('welcome');
    setGameData(null);
  };

  const handleGameComplete = () => {
    setGameState('finished');
    
    // Show success message
    toast.success('🎉 Congratulations! You solved the puzzle!', {
      position: 'top-center',
      autoClose: 5000
    });

    // Auto-return to welcome screen after celebration
    setTimeout(() => {
      setGameState('welcome');
      setGameData(null);
    }, 5000);
  };

  return (
    <div className="App">
      <ToastContainer
        position="top-center"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />

      {gameState === 'welcome' && (
        <WelcomeScreen
          onStartGame={startGame}
          difficultyLevels={config?.difficulty_levels}
        />
      )}

      {gameState === 'loading' && (
        <LoadingScreen difficulty={difficulty} />
      )}

      {gameState === 'playing' && gameData && (
        <GameBoard
          gameData={gameData}
          difficulty={difficulty}
          onRestart={restartGame}
          onComplete={handleGameComplete}
        />
      )}

      {gameState === 'finished' && (
        <div className="completion-screen fade-in">
          <div className="completion-content">
            <div className="completion-icon">🎉</div>
            <h1>Amazing Job!</h1>
            <p>You solved the puzzle!</p>
            <button 
              className="btn-primary"
              onClick={restartGame}
            >
              Play Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;