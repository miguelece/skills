# Examples: architecture read from code

One section per check, in the order `module.yaml` declares them. Each holds a
bad example that shows the defect the check states and a good example, the
nearest correct version, that does not trigger it. The design is read from a
codebase's imports, so each example quotes a few files' import lines, and,
where a check needs one, the rule or record the repository states beside
them. Every example is from the same invented Python repository, `shop/`,
with a `domain`, a `service` and an `api` package.

## architecture-design-from-code/import-cycle

**Bad.** Following the import lines leads from `shop.orders` through
`shop.billing` back to `shop.orders`, and both imports run at import time:

```text
shop/orders/models.py:3     from shop.billing.invoice import Invoice
shop/billing/invoice.py:2   from shop.orders.models import Order
```

**Good.** The shared type moves to a package both import, so neither
imports the other; an import under a type-checking guard would instead be
named as such, not counted as an edge:

```text
shop/orders/models.py:3     from shop.common.ids import OrderId
shop/billing/invoice.py:2   from shop.common.ids import OrderId
shop/common/ids.py          (no imports from shop)
```

## architecture-design-from-code/import-against-stated-layering

**Bad.** The repository states its layers in an import-linter contract, and
a domain module imports from the layer above it:

```text
.importlinter:
    [importlinter:contract:layers]
    name = Layers
    type = layers
    layers =
        shop.api
        shop.service
        shop.domain

shop/domain/order.py:4      from shop.service.pricing import price_of
```

**Good.** The same contract, and the domain module takes the price it needs
as an argument, so it imports nothing above it; the service imports the
domain, which the layering allows:

```text
.importlinter:
    [importlinter:contract:layers]
    name = Layers
    type = layers
    layers =
        shop.api
        shop.service
        shop.domain

shop/domain/order.py        (no imports from shop.service or shop.api)
shop/service/pricing.py:2   from shop.domain.order import Order
```

## architecture-design-from-code/structural-decision-without-confirmation

**Bad.** A decision record states a structural rule, and the files read in
looking for a check of it show none:

```text
docs/adr/0004-domain-has-no-framework-imports.md:
    ## Decision
    Modules under shop/domain import nothing from shop/api or from the
    web framework, Flask.

files read for a confirmation:
    docs/adr/0004-domain-has-no-framework-imports.md  no confirmation section
    .importlinter                                     absent
    pyproject.toml                                    no import-linter section
    tests/                                            no test imports shop.domain
                                                      to assert its imports
```

**Good.** The same record names the check that confirms it, and the check
is in the repository, expressing the rule:

```text
docs/adr/0004-domain-has-no-framework-imports.md:
    ## Decision
    Modules under shop/domain import nothing from shop/api or from the
    web framework, Flask.

    ## Confirmation
    The "Domain is framework-free" contract in .importlinter, run in CI.

.importlinter:
    [importlinter:contract:domain-is-framework-free]
    name = Domain is framework-free
    type = forbidden
    source_modules =
        shop.domain
    forbidden_modules =
        shop.api
        flask
```
