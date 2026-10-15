// N-001: a seat has one holder at a time.
import { holdSeats, HOLD_MINUTES } from "./hold";

test("holds expire after the configured minutes", () => {
  const now = new Date("2026-10-01T10:00:00Z");
  expect(holdSeats("e1", ["A1"], "b1", now).expiresAt.getTime() - now.getTime()).toBe(HOLD_MINUTES * 60_000);
});
