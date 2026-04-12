import React from 'react';
import PropTypes from 'prop-types';
import './UserBar.css';

const AVATARS = { 1: '🦁', 2: '🐼', 3: '🦊', 4: '🐧', 5: '🦋' };

const UserBar = ({ user, onLogout, onHistory, onNewGame, onEditProfile }) => (
  <div className="user-bar">
    <div className="user-bar-info">
      {user ? (
        <>
          <div className="user-menu">
            <button className="user-menu-trigger" aria-label="Open menu">
              <span className="hamburger-bar" />
              <span className="hamburger-bar" />
              <span className="hamburger-bar" />
            </button>
            <div className="user-dropdown">
              <button className="user-dropdown-item" onClick={onNewGame}>
                🎮 New Game
              </button>
              <button className="user-dropdown-item" onClick={onHistory}>
                📜 Game History
              </button>
              <button className="user-dropdown-item" onClick={onEditProfile}>
                ✏️ Edit Profile
              </button>
            </div>
          </div>
          <span className="user-bar-avatar">{AVATARS[user.avatar_id] || '🧩'}</span>
          <span className="user-bar-name">{user.username}</span>
          <span className="user-bar-score">Score: {user.total_score ?? 0}</span>
        </>
      ) : (
        <>
          <span className="user-bar-avatar">🧑</span>
          <span className="user-bar-name">Guest</span>
        </>
      )}
    </div>
    <button className="user-bar-logout" onClick={onLogout}>
      {user ? 'Sign Out' : 'Sign In'}
    </button>
  </div>
);

UserBar.propTypes = {
  user: PropTypes.object,
  onLogout: PropTypes.func,
  onHistory: PropTypes.func,
  onNewGame: PropTypes.func,
  onEditProfile: PropTypes.func,
};

UserBar.defaultProps = {
  user: null,
  onLogout: () => {},
  onHistory: () => {},
  onNewGame: () => {},
  onEditProfile: () => {},
};

export default UserBar;
