import { Button } from "@/components/ui/Button";
import { CONFIG, loadConfig } from "@/config";
import { useAuth } from "@/lib/auth";
import { motion } from "motion/react";
import { Copy, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useEffect, useReducer } from "react";
import { getNetwork } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { nativeShare } from "@/lib/whatsapp";

interface NetworkAgent {
  id: string;
  name: string;
  agent_code: string;
  created_at: string;
  deals_count: number;
  bonus_earned: number;
}

interface NetworkData {
  agent_code: string;
  referred_agents: NetworkAgent[];
  bonus_summary: {
    total_earned: number;
    bonuses_count: number;
    max_bonuses: number;
    completed: boolean;
  };
}

export default function NetworkScreen() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [network, setNetwork] = useState<NetworkData | null>(null);
  const [loading, setLoading] = useState(true);
  const [, rerender] = useReducer(x => x + 1, 0);
  useEffect(() => {
    loadConfig().then(() => rerender());
    getNetwork()
      .then(setNetwork)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const agentCode = network?.agent_code || user?.agent_code || "";

  const handleCopy = () => {
    navigator.clipboard.writeText("https://partners.rivo.ae?ref=" + agentCode);
    toast("Link copied!");
  };

  const handleShare = () => {
    const url = `https://partners.rivo.ae?ref=${agentCode}`;
    const message = CONFIG.MESSAGES.SHARE_TEXT.includes("{url}")
      ? CONFIG.MESSAGES.SHARE_TEXT.replace("{url}", url)
      : CONFIG.MESSAGES.SHARE_TEXT + url;
    nativeShare(message);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-AE", { month: "short", day: "numeric" });
  };

  return (
    <div className="flex flex-col min-h-screen bg-black pb-24">
      <div className="bg-black text-white pt-12 pb-8 px-6 border-b border-zinc-800">
        <div className="text-center">
          <h1 className="text-3xl font-medium tracking-tight text-white mb-6">My network</h1>

          <p className="text-gray-400 text-sm mb-4">Your Referral Code</p>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-6">
            <h2 className="text-4xl font-medium tracking-widest text-white">{agentCode}</h2>
          </div>

          <Button
            className="w-full h-14 font-medium rounded-lg mb-4 text-lg"
            onClick={handleShare}
          >
            Invite your network
          </Button>

          <button
            onClick={handleCopy}
            className="text-sm text-gray-400 flex items-center justify-center hover:text-white transition-colors"
          >
            <Copy className="w-4 h-4 mr-2" />
            Tap to copy link
          </button>

          <div className="mt-6 pt-4 border-t border-zinc-800/50">
            <Link to="/referral-info" className="text-sm font-medium text-rivo-green hover:text-rivo-green/80 transition-colors flex items-center justify-center">
              Know more about the referral program
              <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-8">
        <div>
          <h3 className="font-medium text-lg mb-6 text-white">How it works</h3>
          <div className="space-y-8">
            <div className="flex space-x-5">
              <div className="w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800 text-white flex items-center justify-center font-medium flex-shrink-0 text-sm">1</div>
              <div>
                <h4 className="font-medium text-base text-white">Ask Agents to join Rivo</h4>
                <p className="text-sm text-gray-400 mt-1 leading-relaxed">Share your link with agents in your network.</p>
              </div>
            </div>
            <div className="flex space-x-5">
              <div className="w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800 text-white flex items-center justify-center font-medium flex-shrink-0 text-sm">2</div>
              <div>
                <h4 className="font-medium text-base text-white">They refer mortgages to Rivo</h4>
                <p className="text-sm text-gray-400 mt-1 leading-relaxed">Bonuses unlock on their first {CONFIG.REFERRAL_BONUS.AMOUNTS.length} disbursals.</p>
              </div>
            </div>
            <div className="flex space-x-5">
              <div className="w-8 h-8 rounded-full bg-rivo-green text-black flex items-center justify-center font-medium flex-shrink-0 text-sm">3</div>
              <div>
                <h4 className="font-medium text-base text-white">You both get paid</h4>
                <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                  {CONFIG.REFERRAL_BONUS.AMOUNTS.map((a, i) => `AED ${a.toLocaleString()}`).join(", ")} respectively.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-zinc-900">
            <p className="text-xs text-gray-500">
              *Terms and conditions apply. Bonuses are subject to successful loan disbursal and verification.
              <Link to="/terms" className="text-gray-400 hover:text-white underline ml-1">Read full T&Cs</Link>
            </p>
          </div>
        </div>

        <div>
          <h3 className="font-medium text-lg mb-4 flex items-center text-white">
            <Users className="w-5 h-5 mr-2" />
            Your Network
            {network?.bonus_summary.completed && (
              <span className="ml-2 px-2 py-0.5 bg-rivo-green/10 text-rivo-green text-xs font-medium rounded-full">Completed</span>
            )}
          </h3>

          {loading ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b border-zinc-900 animate-pulse">
                  <div>
                    <div className="h-4 w-24 bg-zinc-800 rounded" />
                    <div className="h-3 w-32 bg-zinc-800 rounded mt-2" />
                  </div>
                  <div className="h-4 w-16 bg-zinc-800 rounded" />
                </div>
              ))}
            </div>
          ) : network?.referred_agents.length === 0 ? (
            <p className="text-gray-500 text-sm py-4">No agents in your network yet. Share your link to start earning bonuses.</p>
          ) : (
            <div className="space-y-4">
              {network?.referred_agents.map((agent) => (
                <div key={agent.id} className={`flex justify-between items-center py-2 border-b border-zinc-900 ${agent.deals_count === 0 ? 'opacity-50' : ''}`}>
                  <div>
                    <h4 className="font-medium text-base text-white">{agent.name || "Agent"}</h4>
                    <p className="text-xs text-gray-500 mt-1">Joined {formatDate(agent.created_at)} • {agent.deals_count}/{network?.bonus_summary.max_bonuses || CONFIG.REFERRAL_BONUS.AMOUNTS.length} Deals</p>
                  </div>
                  <div className="text-right">
                    <span className={`font-medium text-sm ${agent.bonus_earned > 0 ? 'text-rivo-green' : 'text-gray-500'}`}>
                      +AED {agent.bonus_earned}
                    </span>
                    <p className="text-[10px] text-gray-500 uppercase">Bonus</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
