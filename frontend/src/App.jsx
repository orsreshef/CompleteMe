import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Confetti from 'react-confetti';
import './App.css';

import WelcomeScreen from './components/WelcomeScreen/WelcomeScreen';
import ImageSelector from './components/ImageSelector/ImageSelector';
import GameBoard from './components/GameBoard/GameBoard';
import LoadingScreen from './components/LoadingScreen/LoadingScreen';
import LoginScreen from './components/LoginScreen/LoginScreen';
import SignupScreen from './components/SignupScreen/SignupScreen';
import HistoryScreen from './components/HistoryScreen/HistoryScreen';
import EditProfileScreen from './components/EditProfileScreen/EditProfileScreen';
import api from './services/api';

function App() {
  const navigate = useNavigate();

  const [initializing, setInitializing] = useState(true);
  const [user, setUser] = useState(null);
  const [difficulty, setDifficulty] = useState(1);
  const [regionCount, setRegionCount] = useState(1);
  const [gameData, setGameData] = useState(null);
  const [config, setConfig] = useState(null);
  const [lastScore, setLastScore] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    loadConfig();
    // Try to restore session from existing JWT cookie
    api.getMe()
      .then(data => {
        setUser(data.user);
        navigate('/game');
      })
      .catch(() => {
        // No valid JWT — check if the user was in guest mode before the refresh
        if (sessionStorage.getItem('guestMode')) {
          navigate('/game');
        } else {
          navigate('/login');
        }
      })
      .finally(() => {
        setInitializing(false);
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
    navigate('/select');
  };

  // Called from ImageSelector with image params: { query } or {}
  const startGame = async (imageParams = {}) => {
    navigate('/loading');

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
      navigate('/play');

      toast.success('Puzzle created! Find the missing piece! 🧩', {
        position: 'top-center',
        autoClose: 3000
      });

    } catch (error) {
      console.error('❌ Failed to create puzzle:', error);
      toast.error('Failed to create puzzle. Please try again.');
      navigate('/select');
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    navigate('/game');
  };

  const handleGuest = () => {
    sessionStorage.setItem('guestMode', '1');
    setUser(null);
    navigate('/game');
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
    navigate('/login');
  };

  const restartGame = () => {
    setGameData(null);
    navigate('/game');
  };

  const handleGameComplete = async (scoreEarned = 0) => {
    setLastScore(scoreEarned);
    setShowConfetti(true);
    navigate('/finished');


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
      setGameData(null);
      navigate('/game');
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

      <Routes>
        {/* Auth screens */}
        <Route
          path="/login"
          element={
            <LoginScreen
              onLogin={handleLogin}
              onGuest={handleGuest}
              onGoSignup={() => navigate('/signup')}
            />
          }
        />
        <Route
          path="/signup"
          element={
            <SignupScreen
              onLogin={handleLogin}
              onGoLogin={() => navigate('/login')}
            />
          }
        />

        {/* Main game flow */}
        <Route
          path="/game"
          element={
            <WelcomeScreen
              onStartGame={handleSelectDifficulty}
              difficultyLevels={config?.difficulty_levels}
              user={user}
              onLogout={handleLogout}
              onHistory={() => navigate('/history')}
              onNewGame={() => navigate('/game')}
              onEditProfile={() => navigate('/profile')}
            />
          }
        />
        <Route
          path="/select"
          element={
            <ImageSelector
              difficulty={difficulty}
              difficultyName={config?.difficulty_levels?.[difficulty]?.name || `Level ${difficulty}`}
              regionCount={regionCount}
              onStartGame={startGame}
              onBack={() => navigate('/game')}
            />
          }
        />
        <Route
          path="/loading"
          element={<LoadingScreen difficulty={difficulty} />}
        />
        <Route
          path="/play"
          element={
            gameData
              ? <GameBoard
                  gameData={gameData}
                  difficulty={difficulty}
                  onRestart={restartGame}
                  onComplete={handleGameComplete}
                />
              : <Navigate to="/" replace />
          }
        />
        <Route
          path="/finished"
          element={
            <div className="completion-screen fade-in">
              {showConfetti && (
                <Confetti
                  width={window.innerWidth}
                  height={window.innerHeight}
                  recycle={false}
                  numberOfPieces={500}
                  onConfettiComplete={() => setShowConfetti(false)}
                />
              )}
              <div className="completion-content">
                <div className="completion-icon">🎉</div>
                <h1>Amazing Job!</h1>
                <p>You solved the puzzle!</p>
                {user && lastScore > 0 && (
                  <div className="score-earned-badge">
                    +{lastScore} pts
                  </div>
                )}
                <button className="btn-primary" onClick={restartGame}>
                  Play Again
                </button>
              </div>
            </div>
          }
        />

        {/* Game history */}
        <Route
          path="/history"
          element={
            user
              ? <HistoryScreen
                    user={user}
                    onBack={() => navigate('/game')}
                    onLogout={handleLogout}
                    onNewGame={() => navigate('/game')}
                    onEditProfile={() => navigate('/profile')}
                  />
              : <Navigate to="/login" replace />
          }
        />

        {/* Edit profile */}
        <Route
          path="/profile"
          element={
            user
              ? <EditProfileScreen
                  user={user}
                  onUserUpdate={setUser}
                  onLogout={handleLogout}
                  onHistory={() => navigate('/history')}
                  onNewGame={() => navigate('/game')}
                  onDeleteAccount={handleLogout}
                />
              : <Navigate to="/login" replace />
          }
        />

        {/* Redirect bare root to /game */}
        <Route path="/" element={<Navigate to="/game" replace />} />

        {/* Fallback — redirect unknown paths to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
}

export default App;
