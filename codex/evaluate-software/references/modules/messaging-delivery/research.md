---
sources:
  - id: microservices-io-transactional-outbox
    title: "Pattern: Transactional outbox (microservices.io, Chris Richardson)"
    url: https://microservices.io/patterns/data/transactional-outbox.html
    date: 2026-11-26
  - id: aws-transactional-outbox
    title: "Transactional outbox pattern (AWS Prescriptive Guidance, Cloud design patterns)"
    url: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
    date: 2026-11-26
  - id: microservices-io-idempotent-consumer
    title: "Pattern: Idempotent Consumer (microservices.io, Chris Richardson)"
    url: https://microservices.io/patterns/communication-style/idempotent-consumer.html
    date: 2026-11-26
  - id: sqs-at-least-once
    title: "Amazon SQS at-least-once delivery (Amazon SQS Developer Guide)"
    url: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html
    date: 2026-11-26
  - id: rabbitmq-reliability
    title: "Reliability Guide (RabbitMQ 4.4 documentation)"
    url: https://www.rabbitmq.com/docs/reliability
    date: 2026-11-26
  - id: kafka-delivery-semantics
    title: "Design, Message Delivery Semantics (Apache Kafka 4.4 documentation)"
    url: https://kafka.apache.org/44/design/design/
    date: 2026-11-26
  - id: pubsub-exactly-once
    title: "Exactly-once delivery (Google Cloud Pub/Sub documentation)"
    url: https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
    date: 2026-11-26
findings:
  - id: dual-write-loses-or-invents-messages
    claim: >-
      A database write and a message publish made as two separate steps
      cannot be made atomic by ordering them: a crash after the commit and
      before the send loses the message, and a send before a commit that
      then rolls back announces a change that never happened. Storing the
      message in the database in the same transaction as the write, an
      outbox read out by a separate relay or by change data capture, joins
      the two.
    confidence: strong
    sources:
      - microservices-io-transactional-outbox
      - aws-transactional-outbox
  - id: brokers-redeliver-by-default
    claim: >-
      The common brokers deliver at least once by default, so a consumer can
      receive the same message more than once: SQS standard queues may
      return a copy that was not deleted, RabbitMQ redelivers after a failure
      when acknowledgements are used and a publisher's retry can duplicate,
      Kafka's default is at least once, and Pub/Sub delivers duplicates
      unless exactly-once delivery is enabled on the subscription.
    confidence: strong
    sources:
      - sqs-at-least-once
      - rabbitmq-reliability
      - kafka-delivery-semantics
      - pubsub-exactly-once
  - id: consumers-must-be-idempotent
    claim: >-
      A consumer is built so that processing the same message twice has no
      further effect, by recording the ids of the messages it has processed
      and refusing a second copy, by a unique key on what it writes, or by an
      operation that is idempotent of itself; the outbox's relay may also
      publish a message twice, so the consumer of an outbox needs the same.
    confidence: strong
    sources:
      - microservices-io-idempotent-consumer
      - sqs-at-least-once
      - rabbitmq-reliability
      - microservices-io-transactional-outbox
      - aws-transactional-outbox
  - id: exactly-once-needs-a-mechanism
    claim: >-
      Exactly-once is not a property a broker gives a whole system: Kafka
      provides it only from Kafka to Kafka, through transactions with the
      consumer's offset in the same transaction, and writing to an external
      system needs that system's cooperation, such as storing the offset with
      the output; Pub/Sub's exactly-once delivery holds only for pull
      subscriptions within one region and still lets publish-side duplicates
      through. A design that relies on it names the mechanism and its limits.
    confidence: evidenced
    sources: [kafka-delivery-semantics, pubsub-exactly-once]
---

# Research: messaging delivery

Read on 2026-11-26 at each source's own page: the transactional outbox and
idempotent consumer patterns on microservices.io, the transactional outbox
pattern in AWS Prescriptive Guidance, the at-least-once page of the Amazon
SQS Developer Guide, RabbitMQ's Reliability Guide, the delivery semantics
section of Kafka's design documentation and Google Cloud's page on Pub/Sub
exactly-once delivery. None of the pages gives a publication or revision
date, so each `date` is the reading date; the RabbitMQ and Kafka pages are
versioned, and their version is in the title.

The two microservices.io patterns are a practitioner's catalogue, not a
vendor's documentation, so each is cited beside a primary page that states
the same: the AWS guidance for the outbox, and the broker documentation for
redelivery and idempotency. The exactly-once finding is marked `evidenced`
rather than `strong` because each of its two sources states the limits of
its own broker only; that no broker gives exactly-once to a whole system is
read from the two agreeing, not stated by either.

## Whether a reading can verify each candidate

Three candidates were put to this module. All three are kept, each narrowed
until a finding can quote what it rests on.

- **A database write and a publish in one operation with no outbox or
  transaction joining them.** Both halves are calls a reading can quote with
  file and line, and the outbox, when present, is an insert in the same
  transaction, also quotable. What a reading cannot see is a framework that
  routes a publish through an outbox it configures elsewhere, or a write or
  publish behind an abstraction not in the repository; the check names those
  unresolved rather than reporting them. A broker's own transaction is named
  in the evidence as joining nothing, because it is the likeliest thing to be
  mistaken for a fix.
- **A consumer that applies a message's effect with no idempotency key,
  deduplication or upsert.** The handler and its effect are quotable; the
  absence of each listed safeguard is read over the handler and what it
  calls. The check is limited to effects that change the outcome when
  repeated, since an effect idempotent of itself needs no key, and a
  uniqueness constraint in a schema the reading has not seen makes the
  consumer unresolved, not reported. Broker-side deduplication on publish is
  named as not counting, because RabbitMQ and Pub/Sub both show duplicates
  reaching a consumer after it.
- **A design with messaging and no stated delivery guarantee, or one that
  assumes exactly-once without saying how.** A design document is read
  whole, so the absence of a guarantee, or of a mechanism behind an
  exactly-once claim, is a property of the document, quotable as the
  sections describing the messaging.

## Triggers, and what was left out of them

The library covers Python, TypeScript and Go, so the triggers name broker
clients and queue libraries for those three, as markers in `pyproject.toml`,
`requirements.txt`, `package.json` and `go.mod`: AMQP clients for RabbitMQ,
Kafka clients, task queues (Celery, Dramatiq, BullMQ, Bull, Asynq), and the
SQS, Pub/Sub, Azure Service Bus and NATS clients, with Watermill for Go. One
`files` glob, `**/*outbox*`, loads the module on a diff that touches an
outbox. A design loads it by the names of brokers and delivery guarantees
in its prose, or by a heading such as *Messaging* or *Queues*.

- **The whole AWS SDK, `boto3` and `aws-sdk-go`**, are left out: they are
  present in nearly every project on AWS, messaging or not. The SQS-only
  packages, `@aws-sdk/client-sqs` and the Go SDK's `service/sqs`, are kept.
- **Redis clients** are left out: Redis is mostly a cache, and a client's
  presence says nothing of its streams or its pub/sub. A task queue on Redis
  is caught by its own library, BullMQ or Celery.
- **`rq`** is left out: as a substring it matches too many unrelated
  package names to be a marker.
- **`setup.cfg`, `Pipfile`, `poetry.lock` and other Python manifests** are
  left out, as are lockfiles generally: a project that declares its
  dependency in `pyproject.toml` or `requirements.txt` is caught there, and
  the remaining forms would double the list for little reach.
- **Filename globs such as `*consumer*`, `*worker*`, `*handler*` or
  `*events*`** are left out: those names are used for code that has nothing
  to do with a broker, and would load the module on it.
- **An *Events* design heading** is left out for the same reason: it heads
  calendars and audit logs as often as event streams. *Event flow* and
  *Event bus* are kept.
- **Languages the library does not cover**, such as Java or C#, and their
  clients are left out until the library reads those languages.

## What this does not cover

- **Message loss on the consumer side**, a consumer that acknowledges a
  message before it has applied it, so a crash loses it. Kafka's and
  RabbitMQ's pages describe this as at-most-once delivery, but whether an
  acknowledgement precedes the effect turns on each client's auto-ack or
  auto-commit default, which is per library and per version; it belongs in
  a module for each client.
- **Ordering**, a consumer that assumes messages arrive in the order they
  were sent. The AWS outbox page raises it, but no candidate put to this
  module asked for it.
- **Poison messages and dead-letter queues**, retries that never end. They
  are an operational concern of their own.
- **Sagas and distributed transactions across services.** The outbox joins
  one service's write to its message; a transaction spanning several
  services' data is a different pattern, which the AWS page names
  separately.
- **Probing a running system** by crashing it between the write and the
  publish, or by redelivering a message. The static phase runs nothing.
