import { Button } from "@/components/ui/Button";
import { CONFIG, loadConfig } from "@/config";
import { motion } from "motion/react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Activity, Users, Zap } from "lucide-react";
import { useState, useEffect } from "react";
import { initWhatsApp, resolveReferralCode } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { getWhatsAppPref } from "@/lib/whatsapp";
import { WhatsAppShareSheet } from "@/components/ui/WhatsAppShareSheet";

export default function LandingScreen() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [searchParams] = useSearchParams();
  const [referralName, setReferralName] = useState<string | null>(null);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [showPicker, setShowPicker] = useState(false);

  useEffect(() => {
    // If already authenticated, go to home
    if (isAuthenticated) {
      navigate("/home", { replace: true });
      return;
    }
    // Load config from backend
    loadConfig();
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const refCode = searchParams.get("ref");
    if (refCode) {
      localStorage.setItem("rivo_referral_code", refCode);
      resolveReferralCode(refCode)
        .then((data) => setReferralName(data.agent_name))
        .catch(() => setReferralName("Partner Agent"));
    }
  }, [searchParams]);

  // Track if user already had a pref BEFORE the picker opened
  const [wasReturningUser] = useState(() => !!getWhatsAppPref());

  const proceedToWhatsApp = async () => {
    const referralCode = wasReturningUser ? "" : localStorage.getItem("rivo_referral_code") || "";
    try {
      const data = await initWhatsApp(referralCode, false, wasReturningUser);
      localStorage.setItem("rivo_verify_code", data.code);
      localStorage.setItem("rivo_wa_pending", data.whatsapp_url);
      navigate("/whatsapp-verify");
    } catch (err) {
      console.error("Failed to init WhatsApp", err);
    }
  };

  const handleGetStarted = () => {
    if (getWhatsAppPref()) {
      // Pref already saved (returning user) — go straight
      proceedToWhatsApp();
    } else {
      // First time — ask which WhatsApp they use
      setShowPicker(true);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-black p-6 relative">
      {/* Header */}
      <div className="flex justify-between items-start mt-8 mb-12">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-rivo-green rounded-lg flex items-center justify-center">
            <span className="text-black font-medium text-lg">R</span>
          </div>
          <span className="text-xl font-medium text-white tracking-tight">Rivo Partners</span>
        </div>

        {referralName && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2"
          >
            <div className="w-2 h-2 rounded-full bg-rivo-green mr-3 animate-pulse flex-shrink-0" />
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Referred by</span>
              <span className="text-sm font-medium text-white">{referralName}</span>
            </div>
          </motion.div>
        )}
      </div>

      <div className="flex-1 flex flex-col justify-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl font-medium tracking-tight text-white mb-6 leading-[1.1]">
            Earn on every <br />
            <span className="text-rivo-green">mortgage you refer.</span>
          </h1>

          <div className="mt-12 space-y-8">
            <div className="flex items-start space-x-5">
              <Zap className="w-6 h-6 text-rivo-green mt-1" strokeWidth={2} />
              <div>
                <h3 className="text-lg font-medium text-white">Fast Referrals</h3>
                <p className="text-gray-400 text-base leading-relaxed">Submit a client in 60 seconds.</p>
              </div>
            </div>
            <div className="flex items-start space-x-5">
              <Activity className="w-6 h-6 text-rivo-green mt-1" strokeWidth={2} />
              <div>
                <h3 className="text-lg font-medium text-white">Real-Time Tracking</h3>
                <p className="text-gray-400 text-base leading-relaxed">Live updates on every case.</p>
              </div>
            </div>
            <div className="flex items-start space-x-5">
              <Users className="w-6 h-6 text-rivo-green mt-1" strokeWidth={2} />
              <div>
                <h3 className="text-lg font-medium text-white">Network Bonus</h3>
                <p className="text-gray-400 text-base leading-relaxed">Earn by referring other agents.</p>
              </div>
            </div>
          </div>

          <div className="mt-12 py-6 border-t border-zinc-800 border-b">
            <div className="flex items-center space-x-3 mb-1">
              <div className="flex items-baseline space-x-1">
                <span className="text-4xl font-medium tracking-tight text-white">AED {CONFIG.COMMISSION.AVG_PAYOUT.toLocaleString()}<sup className="text-white text-lg font-medium align-super">^</sup></span>
              </div>
              <div className="px-2 py-0.5 rounded-full border border-rivo-green/50 bg-black flex items-center shadow-[0_0_8px_rgba(0,208,132,0.2)]">
                <span className="text-[10px] font-bold text-rivo-green tracking-wide">{CONFIG.COMMISSION.MIN_PERCENT}% - {CONFIG.COMMISSION.MAX_PERCENT}%</span>
              </div>
            </div>
            <p className="text-sm text-gray-500 font-medium">Average payout per deal · on a AED 1.8M loan</p>
          </div>
        </motion.div>
      </div>

      <div className="mt-auto pt-8 space-y-4 z-10">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={agreedToTerms}
            onChange={(e) => setAgreedToTerms(e.target.checked)}
            className="w-5 h-5 rounded border-zinc-700 bg-zinc-900 text-rivo-green focus:ring-rivo-green accent-[#00D084]"
          />
          <span className="text-sm text-gray-400">
            I agree to the{" "}
            <a href="/terms" className="text-rivo-green underline hover:text-rivo-green/80">Terms & Conditions</a>
          </span>
        </label>

        <Button
          variant="whatsapp"
          className={`w-full h-14 text-lg font-bold rounded-lg ${!agreedToTerms ? "opacity-50 pointer-events-none" : ""}`}
          onClick={handleGetStarted}
          disabled={!agreedToTerms}
        >
          <svg className="w-7 h-7 mr-2 text-[#25D366]" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
          </svg>
          Get Started
        </Button>

        <div className="text-center">
          <button
            onClick={handleGetStarted}
            disabled={!agreedToTerms}
            className={`text-sm font-medium text-gray-400 hover:text-white transition-colors ${!agreedToTerms ? "opacity-50 pointer-events-none" : ""}`}
          >
            Already have an account? <span className="underline text-white">Sign In</span>
          </button>
        </div>
      </div>

      <WhatsAppShareSheet
        open={showPicker}
        onClose={() => setShowPicker(false)}
        onSelect={() => proceedToWhatsApp()}
      />
    </div>
  );
}
