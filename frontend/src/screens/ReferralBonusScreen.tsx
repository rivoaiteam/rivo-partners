import { Button } from "@/components/ui/Button";
import { CONFIG, loadConfig } from "@/config";
import { useAuth } from "@/lib/auth";
import { motion } from "motion/react";
import { useNavigate, Link } from "react-router-dom";
import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { nativeShare } from "@/lib/whatsapp";

function ordinal(n: number) {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export default function ReferralBonusScreen() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [, setConfigLoaded] = useState(false);
  useEffect(() => {
    loadConfig().then(() => setConfigLoaded(true));
  }, []);

  const handleShare = () => {
    const url = `https://partners.rivo.ae?ref=${user?.agent_code}`;
    const message = CONFIG.MESSAGES.SHARE_TEXT.includes("{url}")
      ? CONFIG.MESSAGES.SHARE_TEXT.replace("{url}", url)
      : CONFIG.MESSAGES.SHARE_TEXT + url;
    nativeShare(message);
  };

  return (
    <div className="flex flex-col min-h-screen bg-black text-white p-6 relative">
      <button
        onClick={() => navigate("/home")}
        className="absolute top-6 right-6 p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition-colors z-10"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      <div className="flex-1 flex flex-col pt-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-medium tracking-tight mb-6">Refer Agents</h1>

          <p className="text-xl text-gray-300 leading-relaxed mb-12">
            Your network can get you started with Rivo. <br />
            <span className="text-white">They close deals, you get paid.</span>
          </p>

          {/* Timeline Visualization */}
          <div className="relative pl-4 space-y-12">
            <div className="absolute left-[23px] top-4 bottom-4 w-0.5 bg-zinc-800" />

            {CONFIG.REFERRAL_BONUS.AMOUNTS.map((amount, i) => {
              const isLast = i === CONFIG.REFERRAL_BONUS.AMOUNTS.length - 1;
              return (
                <div key={i} className="relative flex items-center">
                  <div className={`w-4 h-4 rounded-full border-2 border-black z-10 mr-6 ${isLast ? 'bg-rivo-green shadow-[0_0_10px_rgba(0,208,132,0.5)]' : 'bg-zinc-800'}`} />
                  <div className="flex-1 flex justify-between items-baseline">
                    <span className={`text-lg font-medium ${isLast ? 'text-white' : 'text-gray-400'}`}>{ordinal(i + 1)} Deal</span>
                    <span className={`text-2xl font-medium ${isLast ? 'text-rivo-green' : 'text-white'}`}>AED {amount.toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-16 pt-8 border-t border-zinc-900">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500 uppercase tracking-wider font-medium">Total Potential</span>
              <span className="text-3xl font-medium text-white tracking-tight">AED {CONFIG.REFERRAL_BONUS.TOTAL_POTENTIAL.toLocaleString()}</span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="mt-auto pt-8 space-y-4">
        <Button
          className="w-full h-14 text-lg font-medium bg-white text-black hover:bg-gray-200 rounded-lg"
          onClick={handleShare}
        >
          Share your link
        </Button>

        <button
          onClick={() => navigate("/home")}
          className="w-full py-4 text-sm font-medium text-gray-500 hover:text-white transition-colors"
        >
          Skip for now
        </button>

        <div className="mt-2 pt-4 border-t border-zinc-800/50">
          <Link to="/referral-info" className="text-sm font-medium text-rivo-green hover:text-rivo-green/80 transition-colors flex items-center justify-center">
            Know more about the referral program
            <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>

    </div>
  );
}
