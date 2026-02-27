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

/** Clear WhatsApp preference (forces picker next time). */
export function clearWhatsAppPref() {
  localStorage.removeItem(PREF_KEY);
}

/**
 * After firing a deep link, verify the app actually opened.
 *
 * - Page never goes hidden within 3s → app not installed → clear pref.
 * - Page goes hidden then returns quickly (<8s) → Play Store bounce → clear pref.
 * - Page goes hidden and stays 8s+ → user was in the real app → pref stays.
 */
function verifyAppOpened() {
  let hiddenAt: number | null = null;

  const handler = () => {
    if (document.visibilityState === "hidden") {
      hiddenAt = Date.now();
    } else if (document.visibilityState === "visible" && hiddenAt) {
      const elapsed = Date.now() - hiddenAt;
      if (elapsed < 8000) {
        // Quick bounce back — Play Store or app didn't open properly
        clearWhatsAppPref();
      }
      // If 8s+ passed, they were actually in WhatsApp — pref stays
      cleanup();
    }
  };

  const cleanup = () => {
    document.removeEventListener("visibilitychange", handler);
    clearTimeout(timeout);
  };

  document.addEventListener("visibilitychange", handler);

  const timeout = setTimeout(() => {
    // 3s passed and page never went hidden — app not installed
    if (!hiddenAt) {
      clearWhatsAppPref();
    }
    cleanup();
  }, 3000);
}

/**
 * Build direct deep link URL for a specific WhatsApp app.
 * No wa.me — targets the exact app so the OS picker never appears.
 */
function buildDeepLink(type: WhatsAppType, params: string): string {
  if (type === "personal") {
    return `whatsapp://send?${params}`;
  }
  if (isIOS()) {
    return `whatsapp-smb://send?${params}`;
  }
  // Android Business: intent with package targeting
  return `intent://send?${params}#Intent;package=com.whatsapp.w4b;end`;
}

/**
 * Open a specific WhatsApp app with a pre-filled share message.
 * Used for referral sharing (no phone number, just text).
 */
export function openWhatsAppDirect(text: string, type: WhatsAppType) {
  const encoded = encodeURIComponent(text);
  window.location.href = buildDeepLink(type, `text=${encoded}`);
  verifyAppOpened();
}

/**
 * Open WhatsApp to chat with a specific phone number.
 * Used for OTP/verification. Uses saved pref for direct deep link.
 */
export function openWhatsAppChat(phone: string, text: string) {
  const pref = getWhatsAppPref();
  const encoded = encodeURIComponent(text);

  if (pref) {
    window.location.href = buildDeepLink(pref, `phone=${phone}&text=${encoded}`);
    verifyAppOpened();
  } else {
    // No pref yet — fallback to wa.me (only during OTP if picker was skipped)
    window.location.href = `https://wa.me/${phone}?text=${encoded}`;
  }
}
