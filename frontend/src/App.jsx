import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

import WelcomeScreen from './components/WelcomeScreen/WelcomeScreen';
import ImageSelector from './components/ImageSelector/ImageSelector';
import GameBoard from './components/GameBoard/GameBoard';
import LoadingScreen from './components/LoadingScreen/LoadingScreen';
import LoginScreen from './components/LoginScreen/LoginScreen';
import SignupScreen from './components/SignupScreen/SignupScreen';
import api from './services/api';

function App() {
  // 'login', 'signup', 'welcome', 'imageSelect', 'loading', 'playing', 'finished'
  const [gameState, setGameState] = useState('login');
  const [initializing, setInitializing] = useState(true);
  const [user, setUser] = useState(null);
  const [difficulty, setDifficulty] = useState(1);
  const [regionCount, setRegionCount] = useState(1);
  const [gameData, setGameData] = useState(null);
  const [config, setConfig] = useState(null);
  const [lastScore, setLastScore] = useState(0);

  useEffect(() => {
    loadConfig();
    // Try to restore session from existing JWT cookie
    api.getMe()
      .then(data => {
        setUser(data.user);
        setGameState('welcome');
      })
      .catch(() => {
        // No valid JWT — check if the user was in guest mode before the refresh
        if (sessionStorage.getItem('guestMode')) {
          setGameState('welcome');
        }
        // else stay on login screen
      })
      .finally(() => {
        setInitializing(false);
      });
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

  // Called from WelcomeScreen after both difficulty and region count are chosen
  const handleSelectDifficulty = (selectedDifficulty, selectedRegionCount) => {
    setDifficulty(selectedDifficulty);
    setRegionCount(selectedRegionCount);
    setGameState('imageSelect');
  };

  // Called from ImageSelector with image params: { query } or {}
  const startGame = async (imageParams = {}) => {
    setGameState('loading');

    try {
      console.log(`🎮 Starting game with difficulty ${difficulty}...`, imageParams);

      const data = await api.createPuzzle({
        difficulty,
        num_regions: regionCount,
        use_random_image: true,
        ...imageParams,
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
      setGameState('imageSelect');
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setGameState('welcome');
  };

  const handleGuest = () => {
    sessionStorage.setItem('guestMode', '1');
    setUser(null);
    setGameState('welcome');
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.warn('Logout request failed, clearing session anyway:', err);
    }
    sessionStorage.removeItem('guestMode');
    setUser(null);
    setGameData(null);
    setGameState('login');
  };

  const restartGame = () => {
    setGameState('welcome');
    setGameData(null);
  };

  const handleGameComplete = async (scoreEarned = 0) => {
    setLastScore(scoreEarned);
    setGameState('finished');

    toast.success('🎉 Congratulations! You solved the puzzle!', {
      position: 'top-center',
      autoClose: 5000
    });

    // Refresh user profile so the score updates immediately in the UI
    if (user) {
      try {
        const data = await api.getMe();
        setUser(data.user);
      } catch {
        // Silent — score will still be correct on next page load
      }
    }

    setTimeout(() => {
      setGameState('welcome');
      setGameData(null);
    }, 5000);
  };

  // Wait for session restore to complete before rendering any screen
  if (initializing) return null;

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

      {gameState === 'login' && (
        <LoginScreen
          onLogin={handleLogin}
          onGuest={handleGuest}
          onGoSignup={() => setGameState('signup')}
        />
      )}

      {gameState === 'signup' && (
        <SignupScreen
          onLogin={handleLogin}
          onGoLogin={() => setGameState('login')}
        />
      )}

      {gameState === 'welcome' && (
        <WelcomeScreen
          onStartGame={handleSelectDifficulty}
          difficultyLevels={config?.difficulty_levels}
          user={user}
          onLogout={handleLogout}
        />
      )}

      {gameState === 'imageSelect' && (
        <ImageSelector
          difficulty={difficulty}
          difficultyName={config?.difficulty_levels?.[difficulty]?.name || `Level ${difficulty}`}
          regionCount={regionCount}
          onStartGame={startGame}
          onBack={() => setGameState('welcome')}
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
            {user && lastScore > 0 && (
              <div className="score-earned-badge">
                +{lastScore} pts
              </div>
            )}
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