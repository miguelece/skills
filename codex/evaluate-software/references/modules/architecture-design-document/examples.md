# Examples: architecture read from a design document

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The input is a design
document, so each example is a short excerpt of one, quoted as the document
would read. Every excerpt is from the same invented design: an order service
that takes orders from a web shop and hands them to a warehouse system.

## architecture-design-document/quality-attribute-without-measure

**Bad.** The design sets out to be fast and available, and nothing in the
document says how either would be judged met:

```markdown
## Quality attributes

The order service must be fast and highly available, and it must scale
with the shop's growth.
```

**Good.** The same attributes, each with a scenario and a measurable
threshold:

```markdown
## Quality attributes

- **Latency.** Under a normal load of 50 orders a second, the service
  accepts an order in under 200 ms at the 99th percentile.
- **Availability.** The service accepts orders 99.9% of each calendar
  month; after the loss of one instance it accepts orders again within
  30 seconds.
- **Scalability.** At four times the normal load, adding instances keeps
  the latency above within its threshold, with no change to the code.
```

## architecture-design-document/decision-without-alternatives

**Bad.** The decision sets how the service talks to the warehouse, a
dependency and an interface, and no other option appears in the section or
anywhere else in the document:

```markdown
## Decision

The order service publishes each accepted order to a Kafka topic, and the
warehouse system consumes it from there.
```

**Good.** The same decision, with the options weighed against it. Why
each rejected option lost is the next check's subject, so it is left out
here:

```markdown
## Considered options

1. Publish each order to a Kafka topic the warehouse consumes.
2. Call the warehouse's HTTP API synchronously when an order is accepted.
3. Write orders to a shared database table the warehouse polls.

## Decision

Option 1: the service publishes each accepted order to a Kafka topic, and
the warehouse system consumes it from there.
```

## architecture-design-document/alternative-without-reason

**Bad.** The alternatives are named, and nothing there, nor in the
decision's justification, says why the synchronous call lost:

```markdown
## Alternatives considered

- **Synchronous HTTP call to the warehouse.** The service calls the
  warehouse's order endpoint while the customer waits.
- **Shared database table.** Rejected: it couples both systems to one
  schema, so neither can change it alone.
```

**Good.** Each alternative carries the reason it was not chosen:

```markdown
## Alternatives considered

- **Synchronous HTTP call to the warehouse.** Rejected: an outage of the
  warehouse would stop the shop taking orders, against the availability
  goal.
- **Shared database table.** Rejected: it couples both systems to one
  schema, so neither can change it alone.
```

## architecture-design-document/decision-without-consequences

**Bad.** The decision lists its results, and every one is a benefit:

```markdown
## Decision

The order service publishes each accepted order to a Kafka topic, and the
warehouse system consumes it from there.

## Consequences

- The shop keeps taking orders while the warehouse is down.
- The warehouse can be scaled and deployed on its own schedule.
```

**Good.** The same results, with the costs the decision takes on beside
them:

```markdown
## Decision

The order service publishes each accepted order to a Kafka topic, and the
warehouse system consumes it from there.

## Consequences

- The shop keeps taking orders while the warehouse is down.
- The warehouse can be scaled and deployed on its own schedule.
- Cost: an order is confirmed to the customer before the warehouse has
  seen it, so a stock shortage is found only later and needs a
  compensating cancellation.
- Cost: the team runs and monitors a Kafka cluster it does not run today.
```

## architecture-design-document/goals-without-non-goals

**Bad.** The goals are stated, and the document says nothing anywhere about
what it leaves out:

```markdown
## Goals

- Accept orders from the web shop and hand them to the warehouse.
- Keep taking orders while the warehouse is unavailable.
```

**Good.** The same goals, with objectives a reader could have assumed in
named as out of scope:

```markdown
## Goals

- Accept orders from the web shop and hand them to the warehouse.
- Keep taking orders while the warehouse is unavailable.

## Non-goals

- Taking payment: the shop's existing payment service keeps that.
- Orders placed by phone or in store, which the warehouse receives today
  by another route and will go on receiving by it.
```
