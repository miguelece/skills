# Examples: messaging delivery

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The concept is
language-neutral, so the code examples are written in one invented
TypeScript service with a SQL client and an AMQP-style channel, trimmed to
the lines the check reads; the design example quotes an invented design
document.

## messaging-delivery/write-and-publish-without-outbox

**Bad.** The order is committed, and the event is published afterwards as a
separate step, so a crash between the two leaves an order no other service
hears of:

```typescript
// src/orders/place.ts
export async function placeOrder(order: Order): Promise<void> {
  await db.transaction(async (tx) => {
    await tx.query("INSERT INTO orders (id, total) VALUES ($1, $2)",
      [order.id, order.total]);
  });
  channel.publish("orders", "order.placed",
    Buffer.from(JSON.stringify(order)));
}
```

**Good.** The event is inserted into an outbox table in the same
transaction as the order, and a separate relay publishes what the outbox
holds. The outbox table is one acceptable form; change data capture on the
orders table would be another:

```typescript
// src/orders/place.ts
export async function placeOrder(order: Order): Promise<void> {
  await db.transaction(async (tx) => {
    await tx.query("INSERT INTO orders (id, total) VALUES ($1, $2)",
      [order.id, order.total]);
    await tx.query(
      "INSERT INTO outbox (id, topic, payload) VALUES ($1, $2, $3)",
      [randomUUID(), "order.placed", JSON.stringify(order)]);
  });
}

// src/outbox/relay.ts
export async function relayOutbox(): Promise<void> {
  const rows = await db.query("SELECT * FROM outbox ORDER BY created_at");
  for (const row of rows) {
    channel.publish("orders", row.topic, Buffer.from(row.payload),
      { messageId: row.id });
    await db.query("DELETE FROM outbox WHERE id = $1", [row.id]);
  }
}
```

## messaging-delivery/consumer-without-idempotency

**Bad.** The consumer charges the customer for each message it receives,
and nothing records that a message was already handled, so a redelivery
charges twice:

```typescript
// src/payments/consumer.ts
channel.consume("order.placed", async (msg) => {
  const order = JSON.parse(msg.content.toString());
  await payments.charge(order.customerId, order.total);
  channel.ack(msg);
});
```

**Good.** The consumer records the message id in a table whose primary key
refuses a second copy, in the same transaction as its own record of the
charge, and passes the order id to the payment provider as its idempotency
key, so a redelivered message changes nothing:

```typescript
// src/payments/consumer.ts
channel.consume("order.placed", async (msg) => {
  const order = JSON.parse(msg.content.toString());
  await db.transaction(async (tx) => {
    const { rowCount } = await tx.query(
      "INSERT INTO processed_messages (id) VALUES ($1) " +
        "ON CONFLICT DO NOTHING",
      [msg.properties.messageId]);
    if (rowCount === 0) return;
    await payments.charge(order.customerId, order.total,
      { idempotencyKey: order.id });
  });
  channel.ack(msg);
});
```

## messaging-delivery/design-without-delivery-guarantee

**Bad.** The design passes events through a broker and promises that each
is handled exactly once, without saying how:

```text
## Messaging
The orders service publishes an order.placed event to Kafka for every new
order. The payments service consumes it and charges the customer. Each
event is processed exactly once.
```

**Good.** The same flow, and the design states the guarantee it relies on
and what the consumer does about it. Stating at-least-once with an
idempotent consumer is one acceptable form; naming a broker feature that
gives exactly-once, with its limits, would be another:

```text
## Messaging
The orders service writes each order.placed event to an outbox table in
the same transaction as the order, and a relay publishes it to Kafka.
Delivery is at least once: the relay or the broker may deliver an event
twice. The payments service records each event id it has processed and
skips a duplicate, and charges with the order id as the payment's
idempotency key.
```
