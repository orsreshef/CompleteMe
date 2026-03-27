import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import api from '../../services/api';
import UserBar from '../UserBar/UserBar';
import './EditProfileScreen.css';

const AVATARS = { 1: '🦁', 2: '🐼', 3: '🦊', 4: '🐧', 5: '🦋' };

const EditProfileScreen = ({ user, onUserUpdate, onLogout, onHistory, onNewGame, onDeleteAccount }) => {
  const [selectedAvatar, setSelectedAvatar] = useState(user?.avatar_id ?? 1);
  const [avatarLoading, setAvatarLoading] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const [deletePassword, setDeletePassword] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleSaveAvatar = async () => {
    if (selectedAvatar === user?.avatar_id) return;
    setAvatarLoading(true);
    try {
      const data = await api.updateAvatar(selectedAvatar);
      onUserUpdate(data.user);
      toast.success('Avatar updated!');
    } catch (err) {
      toast.error(err.message || 'Failed to update avatar.');
    } finally {
      setAvatarLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match.');
      return;
    }
    if (newPassword.length < 6) {
      toast.error('New password must be at least 6 characters.');
      return;
    }
    setPasswordLoading(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      toast.error(err.message || 'Failed to change password.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteLoading(true);
    try {
      await api.deleteAccount(deletePassword);
      toast.success('Account deleted.');
      onDeleteAccount();
    } catch (err) {
      toast.error(err.message || 'Failed to delete account.');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <div className="edit-profile-screen">
      <UserBar user={user} onLogout={onLogout} onHistory={onHistory} onNewGame={onNewGame} />

      <motion.div
        className="edit-profile-container"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="edit-profile-page-title">
          <h1>Edit Profile</h1>
          <p>Manage your account settings</p>
        </div>

        {/* Avatar section */}
        <motion.div
          className="edit-profile-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2 className="edit-card-title">Profile Picture</h2>
          <div className="avatar-grid">
            {Object.entries(AVATARS).map(([id, emoji]) => {
              const numId = Number(id);
              return (
                <button
                  key={id}
                  className={`avatar-option ${selectedAvatar === numId ? 'selected' : ''}`}
                  onClick={() => setSelectedAvatar(numId)}
                >
                  <span className="avatar-emoji">{emoji}</span>
                </button>
              );
            })}
          </div>
          <button
            className="btn-save"
            onClick={handleSaveAvatar}
            disabled={avatarLoading || selectedAvatar === user?.avatar_id}
          >
            {avatarLoading ? 'Saving...' : 'Save Avatar'}
          </button>
        </motion.div>

        {/* Change password section */}
        <motion.div
          className="edit-profile-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="edit-card-title">Change Password</h2>
          <form className="edit-form" onSubmit={handleChangePassword}>
            <div className="form-group">
              <label>Current Password</label>
              <input
                type="password"
                value={currentPassword}
                onChange={e => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                disabled={passwordLoading}
              />
            </div>
            <div className="form-group">
              <label>New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="At least 6 characters"
                disabled={passwordLoading}
              />
            </div>
            <div className="form-group">
              <label>Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                placeholder="Repeat new password"
                disabled={passwordLoading}
              />
            </div>
            <button
              type="submit"
              className="btn-save"
              disabled={passwordLoading || !currentPassword || !newPassword || !confirmPassword}
            >
              {passwordLoading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </motion.div>

        {/* Delete account section */}
        <motion.div
          className="edit-profile-card edit-profile-card--danger"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="edit-card-title edit-card-title--danger">Delete Account</h2>
          <p className="danger-description">
            This will permanently delete your account and all your game history. This cannot be undone.
          </p>

          {!showDeleteConfirm ? (
            <button className="btn-danger-outline" onClick={() => setShowDeleteConfirm(true)}>
              Delete My Account
            </button>
          ) : (
            <div className="delete-confirm-zone">
              <div className="form-group">
                <label>Enter your password to confirm</label>
                <input
                  type="password"
                  value={deletePassword}
                  onChange={e => setDeletePassword(e.target.value)}
                  placeholder="Your password"
                  disabled={deleteLoading}
                />
              </div>
              <div className="delete-confirm-actions">
                <button
                  className="btn-cancel"
                  onClick={() => { setShowDeleteConfirm(false); setDeletePassword(''); }}
                  disabled={deleteLoading}
                >
                  Cancel
                </button>
                <button
                  className="btn-danger"
                  onClick={handleDeleteAccount}
                  disabled={deleteLoading || !deletePassword}
                >
                  {deleteLoading ? 'Deleting...' : 'Yes, Delete Forever'}
                </button>
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
};

EditProfileScreen.propTypes = {
  user:            PropTypes.object.isRequired,
  onUserUpdate:    PropTypes.func.isRequired,
  onLogout:        PropTypes.func,
  onHistory:       PropTypes.func,
  onNewGame:       PropTypes.func,
  onDeleteAccount: PropTypes.func,
};

EditProfileScreen.defaultProps = {
  onLogout:        () => {},
  onHistory:       () => {},
  onNewGame:       () => {},
  onDeleteAccount: () => {},
};

export default EditProfileScreen;
