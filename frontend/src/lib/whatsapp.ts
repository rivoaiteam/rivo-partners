/**
 * Opens WhatsApp with a pre-filled text message (share/referral).
 * Uses wa.me universal link — OS opens whichever WhatsApp the user has.
 */
export function openWhatsAppShare(text: string) {
  const encoded = encodeURIComponent(text);
  window.open(`https://wa.me/?text=${encoded}`, "_blank");
}

/**
 * Opens WhatsApp chat with a specific phone number and pre-filled message.
 * Uses wa.me universal link — OS opens whichever WhatsApp the user has.
 */
export function openWhatsAppChat(phone: string, text: string) {
  const encoded = encodeURIComponent(text);
  window.location.href = `https://wa.me/${phone}?text=${encoded}`;
}
