// src/pages/GoogleLoginPage.tsx
import React, { useEffect } from "react";
import { signInWithPopup } from "firebase/auth";
import { auth, provider } from "../firebase/config";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const GoogleLoginPage: React.FC = () => {
  const { user, userProfile, loading } = useAuth();
  const navigate = useNavigate();

  const handleSignIn = async () => {
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error("Google sign-in failed:", error);
    }
  };

  // Auto-redirect after successful login
  useEffect(() => {
    if (user && userProfile && !loading) {
      console.log("✅ User logged in successfully, redirecting to chat...");
      navigate("/chat");
    }
  }, [user, userProfile, loading, navigate]);

  if (loading) {
    return (
      <div className="text-center mt-20">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (user) {
    return (
      <div className="text-center mt-20">
        <img src={user.photoURL ?? ""} alt="profile" className="rounded-full w-20 mx-auto" />
        <h2>{user.displayName}</h2>
        <p>{user.email}</p>
        <p className="mt-4">Redirecting to chat...</p>
      </div>
    );
  }

  return (
    <div className="text-center mt-20">
      <button
        onClick={handleSignIn}
        className="bg-blue-600 text-white px-6 py-2 rounded shadow"
      >
        Sign in with Google
      </button>
    </div>
  );
};

export default GoogleLoginPage;
