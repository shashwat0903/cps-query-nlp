// src/App.tsx
import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthGuard } from './components/AuthGuard';
import { OnboardingGuard } from './components/OnboardingGuard';
import { Header } from './components/Header';
import Signup from './pages/Auth/Signup';
import Login from './pages/Auth/Login';
import { ChatContainer } from './pages/ChatContainer';
import LandingPage from './pages/LandingPage';
import OnboardingPage from './pages/OnboardingPage';
import StudentView from './pages/StudentView';
import StudentProfile from './pages/StudentProfile';
import { AuthProvider } from "./contexts/AuthContext";
import GoogleLoginPage from "./pages/GoogleLoginPage";
import UserProfilePage from './pages/UserProfilePage';

const App = () => {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/google-login" element={<GoogleLoginPage />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/onboarding"
          element={
            <AuthGuard>
              <OnboardingPage />
            </AuthGuard>
          }
        />
        
        <Route
          path="/student"
          element={
            <AuthGuard>
              <OnboardingGuard>
                <StudentView />
              </OnboardingGuard>
            </AuthGuard>
          }
        />

        {/* ✅ NEW StudentProfile route */}
        <Route
          path="/student-profile"
          element={
            <AuthGuard>
              <OnboardingGuard>
                <StudentProfile />
              </OnboardingGuard>
            </AuthGuard>
          }
        />

        <Route
          path="/profile"
          element={
            <AuthGuard>
              <UserProfilePage />
            </AuthGuard>
          }
        />

        <Route
          path="/chat"
          element={
            <AuthGuard>
              <OnboardingGuard>
                <>
                  <Header />
                  <ChatContainer />
                </>
              </OnboardingGuard>
            </AuthGuard>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
};

export default App;
