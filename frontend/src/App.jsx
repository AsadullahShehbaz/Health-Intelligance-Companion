import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ConversationsProvider } from "./context/ConversationsContext";
import Navbar from "./components/Navbar";
import Chatbox from "./components/ChatBox";
import LoginModal from "./components/LoginModal";
import RegisterModal from "./components/RegisterModal";
import "./App.css";

function AppContent() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  return (
    <>
      <Navbar onOpenLogin={() => setShowLogin(true)} />

      <Chatbox onOpenLogin={() => setShowLogin(true)} />

      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onSwitchToRegister={() => {
            setShowLogin(false);
            setShowRegister(true);
          }}
        />
      )}

      {showRegister && (
        <RegisterModal
          onClose={() => setShowRegister(false)}
          onSwitchToLogin={() => {
            setShowRegister(false);
            setShowLogin(true);
          }}
        />
      )}
    </>
  );
}

function AuthedTree() {
  const { user } = useAuth();
  // Keying the provider by user id remounts all conversation state on
  // sign-in / sign-out / patient switch, so one patient never sees another's
  // threads or messages.
  return (
    <ConversationsProvider key={user?.id || "anon"}>
      <AppContent />
    </ConversationsProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthedTree />
    </AuthProvider>
  );
}

export default App;
