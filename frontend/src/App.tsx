import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/lib/auth";
import { ToastProvider } from "@/components/ui/Toast";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Layout from "@/components/Layout";

const LandingScreen = React.lazy(() => import("@/screens/LandingScreen"));
const ReferralBonusScreen = React.lazy(() => import("@/screens/ReferralBonusScreen"));
const HomeScreen = React.lazy(() => import("@/screens/HomeScreen"));
const ClientsScreen = React.lazy(() => import("@/screens/ClientsScreen"));
const NetworkScreen = React.lazy(() => import("@/screens/NetworkScreen"));
const ProfileScreen = React.lazy(() => import("@/screens/ProfileScreen"));
const LeadSubmissionScreen = React.lazy(() => import("@/screens/LeadSubmissionScreen"));
const ReferralSuccessScreen = React.lazy(() => import("@/screens/ReferralSuccessScreen"));
const WhatsAppListeningScreen = React.lazy(() => import("@/screens/WhatsAppListeningScreen"));
const ReferralInfoScreen = React.lazy(() => import("@/screens/ReferralInfoScreen"));
const TermsScreen = React.lazy(() => import("@/screens/TermsScreen"));
const PrivacyScreen = React.lazy(() => import("@/screens/PrivacyScreen"));
const BonusTermsScreen = React.lazy(() => import("@/screens/BonusTermsScreen"));

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ''}>
    <AuthProvider>
      <ToastProvider>
      <BrowserRouter>
        <Suspense fallback={<div style={{minHeight:'100vh',background:'#000'}} />}>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<LandingScreen />} />
            <Route path="/whatsapp-verify" element={<WhatsAppListeningScreen />} />
            <Route path="/terms" element={<TermsScreen />} />
            <Route path="/privacy" element={<PrivacyScreen />} />
            <Route path="/bonus-terms" element={<BonusTermsScreen />} />
            <Route path="/referral-info" element={<ReferralInfoScreen />} />
            <Route
              path="/referral-bonus"
              element={
                <ProtectedRoute>
                  <ReferralBonusScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <HomeScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/clients"
              element={
                <ProtectedRoute>
                  <ClientsScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/network"
              element={
                <ProtectedRoute>
                  <NetworkScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfileScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/refer-client"
              element={
                <ProtectedRoute>
                  <LeadSubmissionScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/referral-success"
              element={
                <ProtectedRoute>
                  <ReferralSuccessScreen />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
        </Suspense>
      </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
    </GoogleOAuthProvider>
  );
}
