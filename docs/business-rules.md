# Book Worm — Business Rules

## BR-001 — Authentication

Protected user functionality requires authentication.

---

## BR-002 — Cart Quantity

Book quantity must be greater than or equal to 1.

---

## BR-003 — Cart Ownership

A user can only access their own cart.

---

## BR-004 — Wishlist Ownership

A user can only access their own wishlist.

---

## BR-005 — Order Ownership

A user can only view their own orders.

---

## BR-006 — Buy Again

Buy Again shall copy the books and quantities from the selected
previous order into the current user's cart.

---

## BR-007 — Gift Points

A user cannot redeem more points than their available balance.

---

## BR-008 — Gift Points

Gift points are deducted only after a successful purchase.

---

## BR-009 — Payment

An order shall not be considered paid until payment succeeds.

---

## BR-010 — Failed Payment

A failed payment shall not create a successfully paid order.

---

## BR-011 — Order Creation

A successful payment results in order creation.

---

## BR-012 — Cart After Purchase

After successful order creation, the purchased cart items shall
be removed from the active cart.

---

## BR-013 — Cancellation

An order can be cancelled only within 48 hours of creation.

---

## BR-014 — Cancellation

An order that has already been cancelled cannot be cancelled again.

---

## BR-015 — Book Price

Book price cannot be negative.

---

## BR-016 — Rating

Book/review ratings must be within the supported rating range.

---

## BR-017 — Address

Checkout must have a valid delivery address.

---

## BR-018 — Order Items

An order must contain at least one order item.

---

## BR-019 — Recommendation

Recommendations should be based on available customer purchase
history.

For users without purchase history, the system can fall back to
general/popular books.

---

## BR-020 — Product Availability

A book must be available for purchase before it can be added to
the checkout order.