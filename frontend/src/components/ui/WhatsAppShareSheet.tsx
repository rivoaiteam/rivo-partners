import { AnimatePresence, motion } from "motion/react";
import { openWhatsAppDirect, setWhatsAppPref, type WhatsAppType } from "@/lib/whatsapp";

interface WhatsAppShareSheetProps {
  open: boolean;
  onClose: () => void;
  /** If provided, opens WhatsApp with this text after selection. */
  text?: string;
  /** Called after user picks an app (pref is already saved). */
  onSelect?: (type: WhatsAppType) => void;
}

export function WhatsAppShareSheet({ open, onClose, text, onSelect }: WhatsAppShareSheetProps) {
  const handleSelect = (type: WhatsAppType) => {
    setWhatsAppPref(type);
    if (text) {
      openWhatsAppDirect(text, type);
    }
    onSelect?.(type);
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
          />
          <motion.div
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 bg-zinc-900 rounded-t-3xl p-8 z-50 border-t border-zinc-800"
          >
            <div className="w-12 h-1 bg-zinc-700 rounded-full mx-auto mb-8" />

            <div className="text-center mb-8">
              <h3 className="text-xl font-medium text-white mb-2">Continue with WhatsApp</h3>
              <p className="text-gray-400 text-sm">Select your preferred account.</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleSelect("personal")}
                className="flex flex-col items-center justify-center p-6 bg-black border border-zinc-800 rounded-2xl hover:bg-zinc-800 hover:border-zinc-700 transition-all group"
              >
                <div className="w-16 h-16 rounded-[18px] bg-[#25D366] flex items-center justify-center mb-4 shadow-lg group-hover:scale-105 transition-transform">
                  <svg className="w-9 h-9 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                  </svg>
                </div>
                <span className="font-medium text-white text-sm">Personal</span>
              </button>

              <button
                onClick={() => handleSelect("business")}
                className="flex flex-col items-center justify-center p-6 bg-black border border-zinc-800 rounded-2xl hover:bg-zinc-800 hover:border-zinc-700 transition-all group"
              >
                <div className="w-16 h-16 rounded-[18px] bg-[#25D366] flex items-center justify-center mb-4 shadow-lg group-hover:scale-105 transition-transform">
                  <svg className="w-10 h-10" viewBox="0 0 2500 2500" fill="none">
                    <path d="M1912.32,591.45C1743.07,422.05,1518,328.72,1278.17,328.62c-494.13,0-896.28,402-896.48,896.14a894.32,894.32,0,0,0,119.66,448l-127.18,464.4,475.24-124.62a896.07,896.07,0,0,0,428.4,109.08h.37c494.07,0,896.27-402.05,896.47-896.18.09-239.46-93.07-464.63-262.33-634ZM1278.18,1970.3h-.31a744.11,744.11,0,0,1-379.24-103.83l-27.21-16.14-282,74,75.27-274.87L647,1621.23A742.88,742.88,0,0,1,533,1224.81C533.2,814.12,867.46,480,1278.47,480c199,.08,386.1,77.66,526.78,218.46s218.11,327.94,218,527c-.16,410.73-334.41,744.89-745.1,744.89Z" fill="white"/>
                    <path d="M977.6,1658.86c6.31,3.8,19.27,3.8,49,3.77,126.15-.11,235.11-.49,312.62-.49,361.71,0,352.2-380.79,183.08-428.3,24.77-43.88,137.63-126.32,67.83-296.72-69-168.49-365.85-130.25-568.86-130.15-75.12,0-63.88,55.51-63.5,141.81.62,136.69.11,506.67,0,666.61C957.77,1647.81,967.56,1652.79,977.6,1658.86Zm156.51-139.55c34.15,0,114.71,0,183.77-.11,78.2-.12,147.83-36.7,146.09-114.55-1.27-73.33-50.06-97.4-117.78-104.12-64.5.62-138.27.62-212.08.62v218.16Zm0-365.44c136.05-1.87,188.54,5.48,262.82-13.12,51-29,73.34-136.42.29-172.92-50.75-25.35-200.71-16.68-263.11-14.08v200.12Z" fill="white"/>
                  </svg>
                </div>
                <span className="font-medium text-white text-sm">Business</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-full mt-8 py-3 text-gray-500 font-medium hover:text-white transition-colors text-sm"
            >
              Cancel
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
