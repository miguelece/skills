# Prior art: rule metadata and result records

What three established analysers attach to a rule, and what SARIF records for
a result, as the ground the module contract and the report schema stand on.
Read 2026-11-21 from each tool's own documentation; each section names its
source. Where a page did not state something, this file says so rather than
filling it in.

## Semgrep

Source: Semgrep's rule syntax reference,
<https://docs.semgrep.dev/writing-rules/rule-syntax>, and its guide to
contributing to the rule registry,
<https://docs.semgrep.dev/contributing/contributing-to-semgrep-rules-repository>.

- **Required rule fields**: `id`, `message`, `severity`, `languages`, and one
  pattern key. `metadata` is optional and free-form: it changes nothing about
  matching.
- **Severity**: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, with the legacy `INFO`,
  `WARNING` and `ERROR` still accepted as `LOW`, `MEDIUM` and `HIGH`.
- **Registry rules must carry** `technology`, `category` and `references`
  under `metadata`. A `security` rule must add `cwe`, `owasp`, `confidence`,
  `likelihood`, `impact`, `subcategory` and `vulnerability_class`;
  `confidence`, `likelihood` and `impact` each take `LOW`, `MEDIUM` or
  `HIGH`.
- **Every registry rule has a test file** with at least one true positive and
  one true negative, marked by `ruleid:` and `ok:` comments.

*Taken into the contract*: a language list per module, a severity per check,
mandatory references per check, and a confidence scale. Semgrep's confidence
belongs to the rule; here it moves to the report, where a run states how sure
it is after verifying the finding.

## CodeQL

Source: CodeQL's query metadata reference,
<https://codeql.github.com/docs/writing-codeql-queries/metadata-for-codeql-queries/>.

- **Metadata** sits in a comment at the head of each query: `@name`,
  `@description`, `@id`, `@kind` (`problem` or `path-problem`), `@tags`,
  `@precision` (`low`, `medium`, `high`, `very-high`), `@problem.severity`
  (`error`, `warning`, `recommendation`) for queries not about security, and
  `@security-severity`, a score from 0.0 to 10.0, for those tagged
  `security`.
- **The id** is lowercase letters and digits joined by `/` or `-`, unique per
  query; the standard queries use `<language>/<brief-description>`.
  `@previous-id` carries a renamed query's old id.
- The page links to query help files but does not describe their format.

*Taken into the contract*: the `<module-id>/<name>` check id, after CodeQL's
`<language>/<description>` form, and a concept name as the module's analogue
of CodeQL's tags.

## SonarQube

Source: SonarQube Server's rules overview,
<https://docs.sonarsource.com/sonarqube-server/latest/user-guide/rules/overview/>.

- **Two classifications coexist.** The standard experience types a rule as a
  Bug, a Vulnerability, a Code Smell or a Security Hotspot, with severities
  Blocker, Critical, Major, Minor and Info. The multi-quality mode assigns a
  rule to one or more software qualities, Security, Reliability and
  Maintainability, with severities Blocker, High, Medium, Low and Info.
- **Severity is derived**, from the worst outcome's impact and likelihood,
  each high or low: high and high is Blocker, high impact and low likelihood
  Critical or High, low impact and high likelihood Major or Medium, low and low
  Minor or Low.
- The page does not describe the sections of a rule's description.

*Taken into the contract*: a five-step severity scale ending in `info`, and
the rationale as a required field, since a rule that cannot say why it
matters cannot be weighed against the cost of fixing it.

## SARIF

Source: SARIF 2.1.0, the OASIS standard,
<https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html>,
GitHub's account of the subset its code scanning reads,
<https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning>,
and the OASIS JSON schema,
<https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json>,
read for `reportingConfiguration` and `configurationOverride` because the
standard's page reached the fetcher truncated after section 3.38.

- **A run** names its tool in `tool.driver`, with the tool's rules as
  `reportingDescriptor` objects in `rules[]`: an `id`, a `name`, a
  `shortDescription`, a `fullDescription`, `help`, a
  `defaultConfiguration.level`, and `properties` that GitHub reads for
  `tags`, `precision`, `problem.severity` and `security-severity`. A run's
  `invocations` record how the tool was started.
- **A result** carries a `ruleId`, an optional `level` overriding the rule's
  default, a `message.text`, and `locations[]`, each a `physicalLocation`
  with an `artifactLocation.uri` and a `region` of start and end lines and
  columns. `codeFlows` and `relatedLocations` carry supporting locations, and
  `partialFingerprints` let a consumer match a result across runs.
- **Level and kind**, closely paraphrased, with the standard's words quoted
  only briefly:
  - `result.kind` (3.27.9) takes `pass` (evaluated, no problem found), `open`
    (evaluated, too little information to decide), `informational` (does
    "not indicate a problem"), `notApplicable` (not evaluated, because the
    rule does not apply to the target), `review` (a person must decide) and
    `fail` (a problem, its severity in `level`). Absent, it is `fail`.
  - `result.level` (3.27.10) takes `error` ("a serious problem"), `warning`
    (a problem), `note` (a minor problem, or an opportunity to improve the
    code) and `none` (severity does not apply, because `kind` is not `fail`).
    **A level other than `none` requires `kind` to be `fail`.** Absent, it is
    `none` when `kind` is not `fail`; otherwise the invocation's
    `ruleConfigurationOverrides`, then the rule's
    `defaultConfiguration.level`, then `warning`.
  - `location.logicalLocations` (3.28.4) is an array of `logicalLocation`
    objects (3.33) naming the construct a location lies in, allowed beside
    its `physicalLocation`. A `logicalLocation` has `name`,
    `fullyQualifiedName` (3.33.5: should be present below top level, and
    defaults to `name` at top level), `decoratedName`, `kind`, `index` and
    `parentIndex`; its `kind` (3.33.7) has well-known values such as
    `function`, `member`, `module`, `namespace` and `type`, and allows a
    tool's own.
  - **A rule not run** has a second home besides `kind`: an invocation's
    `ruleConfigurationOverrides` holds `configurationOverride` objects whose
    `reportingConfiguration.enabled` (default `true`) says whether the rule
    could report in that scan.

*Taken into the report schema*: a finding is a result, its check the
`ruleId`, its file the artifact location, its symbol a logical location, and
the run's loaded modules the tool's rules. What SARIF has no field for, the
schema adds: the input kind, the phases requested and run, the modules
skipped and why, and a design-document section as a location. Against the
values above:

- **A finding is a `fail` result.** Every check's `statement` is a defect,
  so `critical` and `high` are `error`, `medium` is `warning`, and `low` and
  `info` are `note`: two serious steps, one middle step and two minor steps,
  as SARIF defines its levels. `info` is not `informational` with level
  `none`, because a check cannot state something that is not a problem.
- **Tools disagree on where `high` falls**, and no standard fixes it: zizmor
  maps High to `error` and Medium to `warning`, while Contrast maps Critical
  to `error`, High to `warning`, and Medium and Low to `note`. Read
  2026-11-22. zizmor's documentation does not state its mapping, so it was
  read from the `From<Severity> for ResultLevel` impl in its source at 1.24.1,
  <https://docs.rs/crate/zizmor/1.24.1/source/src/output/sarif.rs>.
  Contrast's comes from its support article,
  <https://support.contrastsecurity.com/hc/en-us/articles/37626865239700-How-do-Assess-severities-map-to-SARIF-severities>,
  which refused an automated fetch, so its table was read from search
  excerpts of that page. SARIF's "serious problem" decides it here.
- **`location.symbol` is `locations[].logicalLocations[].fullyQualifiedName`**,
  allowed beside a `file` as a logical location is beside a physical one.
- **A skipped module is SARIF's `notApplicable` at module grain**, since the
  module contract declares applicability per module only. A SARIF writer
  would emit it per check, or as `enabled: false` overrides, from
  `modules.skipped` without a schema change.
- **`pass` is implied** by a loaded module with no finding, since every check
  of a loaded module runs.
- **`open` and `review` are what the evidence rule keeps out of the report**:
  a finding that cannot show its evidence is not reported, and a finding's
  low `confidence` carries the doubt that survives verification.
- **`informational` has no use**, since every check states a defect.

## What the survey settled

- **Per-check rationale and references**, required, as Semgrep's registry and
  SonarQube both require of a rule.
- **A language scope per module**, as every tool scopes a rule.
- **A run-level account of what was loaded**, which none of the three keeps
  and an open library needs, since a reader cannot otherwise tell a clean
  result from a module that never ran.
- **Tests per rule** are Semgrep's practice; here the module contract suite
  checks a module's shape, and whether its checks catch real defects is left
  to the owner's review at publish.
