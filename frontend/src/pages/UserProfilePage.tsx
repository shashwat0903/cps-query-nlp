import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfilePage: React.FC = () => {
  const { userProfile, loading } = useAuth();

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!userProfile) {
    return <div className="flex justify-center items-center h-screen">User not found</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-md mx-auto bg-white rounded-lg border border-gray-200 shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4">User Profile</h1>
        <div className="space-y-2">
          <p><strong>Name:</strong> {userProfile.full_name}</p>
          <p><strong>Email:</strong> {userProfile.email}</p>
          <div>
            <p className="font-bold">Completed Topics:</p>
            {userProfile.completed_topics.length > 0 ? (
              <ul className="list-disc list-inside pl-4">
                {userProfile.completed_topics.map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>
            ) : (
              <p>No topics completed yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;
