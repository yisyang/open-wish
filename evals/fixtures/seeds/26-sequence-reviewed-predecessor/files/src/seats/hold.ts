// Seat holds: one holder per seat, released automatically after HOLD_MINUTES.
export const HOLD_MINUTES = 10;

export function holdSeats(eventId: string, seatIds: string[], buyerId: string, now: Date): { expiresAt: Date } {
  // Persistence omitted in this fixture; the delivered module records holds atomically.
  return { expiresAt: new Date(now.getTime() + HOLD_MINUTES * 60_000) };
}
