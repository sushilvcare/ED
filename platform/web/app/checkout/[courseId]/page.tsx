"use client";

import { useState } from "react";

import { apiRequest } from "../../../lib/api";

type PageProps = {
  params: { courseId: string };
};

export default function CheckoutPage({ params }: PageProps) {
  const [token, setToken] = useState("");
  const [orderId, setOrderId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function createOrder() {
    setError(null);
    try {
      const order = await apiRequest<{ id: string }>("/orders/create", {
        method: "POST",
        token,
        body: { course_id: params.courseId },
      });
      setOrderId(order.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create order");
    }
  }

  return (
    <section>
      <h1>Checkout</h1>
      <p>Course ID: {params.courseId}</p>
      <p>Stripe/Razorpay integration placeholder. For now admin marks order paid.</p>
      <label>
        Access token
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Bearer token" />
      </label>
      <button onClick={createOrder}>Create Order</button>
      {orderId ? <p>Order created: {orderId}</p> : null}
      {error ? <p>{error}</p> : null}
    </section>
  );
}
