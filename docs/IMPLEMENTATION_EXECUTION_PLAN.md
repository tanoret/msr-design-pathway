# Project-MSR implementation execution plan - v4.3.0

## Purpose

Version 4.3 converts the WBS from an engineering/licensing scope dictionary into an execution-oriented plan. Every task now identifies how it will be delivered, where the work occurs, what must be procured, which authorizations and hold points apply, which records prove completion, and what fallback is used if the preferred facility, supplier, input, or result is unavailable.

## Implementation standard for every task

Each task implementation plan includes:

- implementation readiness and summary
- owner-led delivery strategy and make/buy/partner split
- authorization and prerequisite evidence
- at least five detailed implementation steps with location, inputs, tools, outputs, acceptance and hold point
- procurement and contracting actions
- long-lead items and capacity reservations
- decisions, owners, need dates and closure evidence
- laboratory, field or vendor activities
- contingencies and alternate routes
- implementation records, source basis and open decisions

## Cross-cutting playbooks

### PB-FUEL-01 - Fuel supply, ownership, fuel-salt production, transport, receipt, and disposition

Obtain the authorized fissile material and convert it into accepted fuel salt on the schedule needed for the INL experiment, demonstrator, and commercial plant without relying on a single uncontracted source.

1. Requirements and supply strategy
2. DOE allocation and commercial backup
3. Enrichment, deconversion, and fissile-feed contracting
4. Fuel-salt synthesis and analytical qualification
5. Production, packaging, transport, receipt, and storage
6. Commercial supply continuity and disposition

**Linked WBS activities:** `S-INL-05`, `S-MSR-06`, `D-DEMO-04`, `D-3.4.g`, `D-3.14.f`, `P-PKG-02`, `P-3.4.g`, `P-3.14.f`, `P-OPT-06`

### PB-CHEM-01 - Fuel-salt chemistry, processing, fission-product management, and analytical validation

Establish the chemistry operating envelope and qualify the minimum practical salt preparation, sampling, monitoring, off-gas, cleanup, and processing functions using a staged progression from nonradioactive surrogates to authorized fuel salt and irradiated confirmation.

1. supplier/feed qualification and carrier-salt purification
2. property, phase, redox, and sensor method qualification
3. static and flowing corrosion/mass-transfer tests
4. fission-product surrogate speciation, plate-out, off-gas, filtration, and capture tests
5. processing architecture down-select and integrated skid repeated-cycle demonstration
6. sampling, online monitoring, MC&A, waste, and maintainability qualification
7. irradiated-salt confirmation using the INL experiment
8. coupled validation in the 2029 demonstrator campaign

**Linked WBS activities:** `D-3.9.f`, `D-EXP-14`, `D-DEMO-03`, `D-DEMO-04`, `D-DEMO-09`, `D-RD-01`, `D-RD-02`, `D-EXP-09`, `D-EXP-10`, `D-EXP-12`, `P-3.11.b`, `P-3.11.g`, `P-7.i`, `P-OPT-04`, `P-OPT-06`, `P-PKG-02`, `S-INL-05`, `S-INL-19`, `S-ITHF-18`, `S-ITHF-28`, `S-ITHF-39`, `S-ITHF-40`, `S-ITHF-45`, `S-MSR-02`, `S-MSR-04`, `S-MSR-05`, `S-MSR-06`, `S-MSR-07`, `S-MSR-09`, `S-MTH-04`, `S-MTH-05`

### PB-FP-01 - Fission-product transport, off-gas, plate-out, capture, and source-term execution

Quantify where fission products reside, how they move, and which treatment functions are required, using surrogate flow/off-gas campaigns followed by irradiated-salt and demonstrator confirmation.

1. group species by chemical/physical behavior
2. build gas/salt/deposit/filter mass balance
3. validate noble-gas transfer and residence time
4. validate aerosol and volatile-species capture
5. validate noble-metal plate-out and resuspension
6. confirm with irradiated samples
7. release mechanistic source-term parameters and uncertainty

**Linked WBS activities:** `S-MSR-04`, `S-MTH-04`, `D-RD-01`, `S-ITHF-40`, `S-INL-19`, `D-EXP-10`, `P-3.11.b`

### PB-MAT-01 - Salt-wetted materials, corrosion, joining, irradiation, and surveillance execution

Qualify alloys, weldments, coatings, seals, graphite/ceramics, and inspection methods across chemistry, temperature, flow, radiation, and fission-product conditions.

1. traceable material heat and joining matrix
2. static capsule screening
3. flowing thermal-gradient exposure
4. fission-product/impurity perturbation
5. mechanical/NDE/repair qualification
6. irradiation and PIE where required
7. life model and surveillance-coupon program
8. commercial ISI/repair implementation

**Linked WBS activities:** `D-RD-02`, `S-MTH-05`, `S-MSR-09`, `S-ITHF-17`, `S-ITHF-45`, `P-PKG-02`, `P-OPT-04`

### PB-MCA-01 - Liquid-fuel material control, accounting, safeguards, and inventory reconciliation

Establish measurement points, material balance areas, sampling, uncertainty, transfer records, anomaly resolution, physical inventory, and dynamic accountancy for fuel distributed among salt, gas, deposits, samples, processing equipment, waste, and storage.

1. define material balance areas and key measurement points
2. qualify mass/volume/composition measurements
3. validate dynamic inventory model with surrogate and qualification batches
4. integrate off-gas/deposit/sample/process inventories
5. perform anomaly and loss-detection exercises
6. qualify receipt/transfer/physical inventory procedures
7. confirm with critical-experiment and demonstrator data

**Linked WBS activities:** `S-MSR-06`, `S-INL-05`, `D-DEMO-04`, `D-3.14.f`, `P-3.14.f`

### PB-WASTE-01 - Salt-processing waste, used salt, deactivation, and final disposition

Provide an authorized path for every residual salt, sample, filter, sorbent, deposit, corrosion product, contaminated component, and decommissioning waste stream before the activity that creates it begins.

1. waste stream forecast
2. characterization and material-accountability interface
3. treatment/conditioning and package selection
4. storage and transport authorization
5. DOE return or licensed disposal route
6. deactivation/decontamination plan
7. cost and records closeout

**Linked WBS activities:** `D-DEMO-09`, `D-3.9.f`, `P-3.11.g`, `P-OPT-06`, `S-ITHF-46`, `S-INL-20`

### PB-TEST-01 - Experimental facility, test campaign, data qualification, and model-validation execution

Use a staged evidence ladder: bench/separate-effects, ITHF, INL critical experiment, demonstrator, and commercial startup, with blind predictions and qualified datasets at each step.

1. PIRT and validation requirements
2. facility/test article definition
3. measurement uncertainty and pre-test predictions
4. commissioning and readiness review
5. campaign execution and exception control
6. independent data qualification
7. model validation and discrepancy closure
8. topical/application evidence release

**Linked WBS activities:** `S-ITHF-02`, `S-ITHF-34`, `S-ITHF-41`, `S-ITHF-42`, `S-ITHF-43`, `S-INL-18`, `S-INL-19`, `D-EXP-14`

### PB-SUPPLY-01 - Supplier qualification, long-lead procurement, manufacturing, and turnover

Translate design requirements into executable supplier packages, reserve capacity early, verify manufacturing at source, and receive complete hardware and records without relying on final inspection alone.

1. market survey and RFI
2. make/buy/partner decision
3. supplier qualification and capacity reservation
4. technical bid evaluation
5. staged supplier design reviews
6. source surveillance and FAT
7. shipping/receiving/preservation
8. installation and turnover
9. second-source and obsolescence plan

**Linked WBS activities:** `S-0.2.d`, `S-ITHF-24`, `S-ITHF-25`, `S-INL-13`, `D-DEMO-07`, `P-PKG-01`, `P-PKG-03`

### PB-HOST-01 - Demonstrator host selection, site integration, authorization and construction execution

Select and contract a host whose existing site, services, nuclear-safety organization, material authority and construction interfaces can support the December 2028 build and 2029 operation without late redesign.

1. define host/site screening criteria and required services
2. issue host RFI and data request
3. perform site/authorization/utilities/security/material due diligence
4. select host and execute responsibilities/IP/liability/services agreement
5. freeze interfaces and site modifications
6. complete DOE/host authorization and construction readiness
7. execute system-based construction turnover and commissioning
8. maintain authorization basis through operation and closeout

**Linked WBS activities:** `D-LP2-03U`, `D-LP2-03I`, `D-LP2-04`, `D-LP2-05`, `D-LP2-11`, `D-LP2-12`, `D-LP2-14`, `D-LP2-15`, `D-LP2-16`

### PB-FACILITY-01 - Experimental facility design, procurement, commissioning, operation and data release

Deliver the ITHF and other experimental systems through requirements/PIRT, scaling, staged design release, long-lead procurement, supplier FAT, site installation, dry/hot commissioning, controlled campaigns, qualified data and facility end state.

1. PIRT and validation requirements
2. facility/site/utilities selection
3. scaling and test-article definition
4. preliminary design and hazard review
5. long-lead and detailed design release
6. fabrication/FAT and source surveillance
7. installation/turnover
8. dry and representative-salt commissioning
9. test readiness and campaign execution
10. data qualification/model validation
11. maintenance/end-state/lessons learned

**Linked WBS activities:** `S-ITHF-01`, `S-ITHF-02`, `S-ITHF-05`, `S-ITHF-23`, `S-ITHF-24`, `S-ITHF-25`, `S-ITHF-28`, `S-ITHF-34`, `S-ITHF-41`, `S-ITHF-42`, `S-ITHF-43`, `S-ITHF-45`

### PB-STARTUP-01 - Fuel receipt, startup, experiment execution, data qualification and operations handoff

Progress from construction turnover through non-fuel commissioning, fuel receipt and loading, initial chemistry/material balance, criticality, controlled operating plateaus, experiment campaigns, anomaly control, qualified data release and final operating/end-state handoff.

1. system turnover and prerequisite verification
2. dry and representative-salt functional testing
3. fuel package receipt/storage acceptance
4. fuel loading and initial material/chemistry baseline
5. criticality/readiness authorization
6. low-power and staged operating plateaus
7. planned chemistry/source-term/material/TH campaigns
8. exception/CAP and retest control
9. qualified data/model update
10. operations or end-state handoff

**Linked WBS activities:** `D-3.14.f`, `D-13.c`, `D-EXP-04`, `D-EXP-06`, `D-EXP-09`, `D-EXP-10`, `D-EXP-12`, `D-EXP-14`, `P-3.14.f`, `P-13.c`

## Bespoke high-consequence work packages

The following packages do not rely on the generic implementation template. They contain activity-specific steps, facilities, inputs, equipment, records, acceptance and hold points:

- `S-INL-05` - fuel requirements, DOE allocation, commercial backup, synthesis/analysis, production, transport, receipt and disposition
- `S-MTH-04` - chemistry/property/source-term/off-gas method qualification and topical report
- `S-MSR-02` - thermophysical property measurement, correlations, covariance and controlled data release
- `S-MSR-04` - fission-product mass balance, surrogate tests, irradiated confirmation and source-term model release
- `S-MSR-05` - online chemistry/off-gas instrumentation and representative hot sampling
- `S-MSR-06` - material balance areas, measurement control, dynamic accountancy and anomaly exercises
- `S-MSR-09`, `S-MTH-05`, `D-RD-02` - materials, joining, corrosion, irradiation, NDE, surveillance and repair qualification
- `D-RD-01` - complete 25-test chemistry and processing pilot
- `D-DEMO-04` - installed demonstrator salt receipt, transfer, sampling, off-gas, processing, drain/recovery, MC&A and waste system
- `D-EXP-02`, `D-EXP-04`, `D-EXP-09`, `D-EXP-10`, `D-EXP-12` - instrumentation/data, initial chemistry baseline, chemistry/fission-product, source-term and materials campaigns
- `S-INL-19` - blind prediction, data qualification, model discrepancy closure and design-data release
- `D-3.14.f`, `P-3.14.f` - pre-shipment review, receipt, custody, storage, rehearsal and fuel-load readiness
- `P-PKG-02` - commercial capacity reservation, production-facility qualification, first articles, materials qualification and startup readiness
- `P-OPT-06` - controlled post-startup fuel, salt, consumables and waste optimization

The program-level decisions that remain open are maintained in `docs/IMPLEMENTATION_GAP_REGISTER.md` and the application Closure register tab. The full 937-row implementation audit is in `data/implementation_task_audit_v4_3.csv`.

## Evidence hierarchy

1. supplier/feed qualification and bench methods
2. separate-effects and engineering-scale testing
3. integral thermal-hydraulics and process-skid testing
4. INL critical experiment and authorized irradiated-salt confirmation
5. 2029 demonstrator coupled operation and experiments
6. commercial construction/startup acceptance and operating feedback

The least hazardous and least expensive evidence is used first. Uranium-bearing or irradiated work is reserved for questions that cannot be closed credibly with stable surrogates and is executed only in an authorized facility.

## Accounting rule

Implementation playbooks and experiment rows are execution crosswalks to existing accounting tasks. They are not additional cost lines and must not be summed a second time. Supplier quotations, laboratory work orders, DOE/host terms and commercial capacity agreements trigger the next cost rebaseline.

