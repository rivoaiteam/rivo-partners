const PREF_KEY = "rivo_whatsapp_pref";

export type WhatsAppType = "personal" | "business";

export function isIOS(): boolean {
  return /iPhone|iPad|iPod/i.test(navigator.userAgent);
}

export function isAndroid(): boolean {
  return /Android/i.test(navigator.userAgent);
}

/** Read saved WhatsApp preference from localStorage. */
export function getWhatsAppPref(): WhatsAppType | null {
  const v = localStorage.getItem(PREF_KEY);
  return v === "personal" || v === "business" ? v : null;
}

/** Save WhatsApp preference. */
export function setWhatsAppPref(type: WhatsAppType) {
  localStorage.setItem(PREF_KEY, type);
}

/**
 * Open a specific WhatsApp app via direct deep link.
 * No wa.me — fires the exact app so the OS picker never appears.
 *
 * Personal:  whatsapp://send?text=...  (both platforms)
 * Business:  whatsapp-smb://send?text=...  (iOS)
 *            intent://send?text=...#Intent;package=com.whatsapp.w4b;end  (Android)
 */
export function openWhatsAppDirect(text: string, type: WhatsAppType) {
  const encoded = encodeURIComponent(text);

  if (type === "personal") {
    window.location.href = `whatsapp://send?text=${encoded}`;
  } else {
    if (isIOS()) {
      window.location.href = `whatsapp-smb://send?text=${encoded}`;
    } else {
      // Android intent targets the exact package
      window.location.href = `intent://send?text=${encoded}#Intent;package=com.whatsapp.w4b;end`;
    }
  }
}

/**
 * Opens WhatsApp chat with a specific phone number and pre-filled message.
 * Used for OTP/verification only — wa.me is fine here since the backend
 * controls which number to message (not a share action).
 */
export function openWhatsAppChat(phone: string, text: string) {
  const encoded = encodeURIComponent(text);
  window.location.href = `https://wa.me/${phone}?text=${encoded}`;
}
