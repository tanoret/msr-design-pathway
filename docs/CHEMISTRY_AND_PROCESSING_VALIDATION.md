# Project-MSR chemistry, salt processing, and fission-product validation plan - v4.3.0

Establish the chemistry operating envelope and qualify the minimum practical salt preparation, sampling, monitoring, off-gas, cleanup, and processing functions using a staged progression from nonradioactive surrogates to authorized fuel salt and irradiated confirmation.

## Processing architecture decision

**Question:** How much online or batch fuel-salt processing is actually required?

**Alternatives**

- no routine salt processing beyond initial purification
- off-gas and particulate control only
- targeted removal of selected chemical groups
- broader fuel-salt processing

**Decision criteria**

- reactivity and fuel utilization
- corrosion and chemistry control
- mechanistic source term and dose
- safeguards and material accountancy
- waste and secondary streams
- operability and maintainability
- capital and lifecycle cost
- licensing and proliferation-resistance implications

**Required date:** 2027-12-31 for demonstrator configuration freeze

Do not assume continuous fission-product extraction. Select the least complex architecture that meets safety, chemistry, reactivity, source-term, safeguards, and economic needs. Radioactive confirmation is performed only in authorized facilities after surrogate down-selection.

## Evidence ladder

1. supplier/feed qualification and carrier-salt purification
2. property, phase, redox, and sensor method qualification
3. static and flowing corrosion/mass-transfer tests
4. fission-product surrogate speciation, plate-out, off-gas, filtration, and capture tests
5. processing architecture down-select and integrated skid repeated-cycle demonstration
6. sampling, online monitoring, MC&A, waste, and maintainability qualification
7. irradiated-salt confirmation using the INL experiment
8. coupled validation in the 2029 demonstrator campaign

## Experiment index

| ID | Campaign | Material stage | Window | Primary decision |
|---|---|---|---|---|
| CHEM-01 | Incoming salt/feed qualification | nonradioactive carrier salt first; authorized fissile feed for production acceptance | Q4 2026-Q2 2027 | fuel-salt acceptance specification; corrosion and redox basis |
| CHEM-02 | Carrier-salt purification scale-up | nonradioactive carrier salt | Q1-Q4 2027 | salt preparation design; fuel-salt synthesis readiness; corrosion control |
| CHEM-03 | Fuel-salt synthesis batch repeatability | surrogate/non-fissile, then authorized uranium-bearing qualification batch | Q2 2027-Q2 2028 | fuel production authorization; batch acceptance; material accountancy |
| CHEM-04 | Phase and freeze-thaw behavior | nonradioactive and authorized uranium-bearing samples as needed | Q1 2027-Q4 2028 | freeze/drain models; storage and transfer design; operating limits |
| CHEM-05 | Thermophysical property matrix | nonradioactive and authorized uranium-bearing specimens | Q4 2026-Q2 2029 | system TH; heat transfer; freeze/drain; source term |
| CHEM-06 | Redox sensor calibration and reference-electrode qualification | nonradioactive salt; later authorized fuel salt confirmation | Q1 2027-Q2 2029 | chemistry action levels; corrosion protection; process control |
| CHEM-07 | Impurity perturbation and recovery | nonradioactive representative salt | Q2 2027-Q4 2028 | abnormal operating procedure; chemistry limits; cleanup system sizing |
| CHEM-08 | Static corrosion matrix | nonradioactive representative salt and surrogates | Q4 2026-Q4 2029 | materials down-select; corrosion model; surveillance plan |
| CHEM-09 | Flow-assisted corrosion and mass transfer | nonradioactive representative salt | Q2 2027-Q4 2029 | loop material selection; inspection locations; maintenance intervals |
| CHEM-10 | Weld, joint, seal, and heat-affected-zone qualification | nonradioactive representative salt | Q2 2027-Q4 2032 | fabrication specifications; repair procedures; ISI basis |
| CHEM-11 | Fission-product surrogate solubility and speciation | stable nonradioactive surrogates first | Q2 2027-Q2 2029 | fission-product transport; processing architecture; source term |
| CHEM-12 | Noble-metal surrogate plate-out | stable surrogates | Q3 2027-Q4 2029 | plate-out model; shielding/maintenance; sampling and cleanup locations |
| CHEM-13 | Stable noble-gas stripping and residence time | stable noble-gas tracers | Q2 2028-Q2 2029 | off-gas sizing; xenon/precursor models; source term |
| CHEM-14 | Aerosol generation, transport, and capture | nonradioactive surrogates | Q3 2027-Q3 2029 | off-gas train design; source term; filter replacement/waste |
| CHEM-15 | Volatile-halogen surrogate capture | stable surrogates | Q3 2027-Q4 2029 | off-gas design; source term; waste classification |
| CHEM-16 | Alkali/cesium surrogate capture | stable surrogates | Q4 2027-Q4 2029 | off-gas/source-term model; maintenance and waste |
| CHEM-17 | Particulate filtration and cleanup | nonradioactive salt and surrogates | Q2 2027-Q3 2028 | cleanup system design; operating action levels; waste handling |
| CHEM-18 | Targeted rare-earth/lanthanide removal down-select | stable nonradioactive surrogates; authorized uranium-bearing confirmation only if needed | Q2 2027-Q4 2027 | processing architecture decision; fuel utilization; safeguards and waste |
| CHEM-19 | Integrated salt-processing skid repeated-cycle demonstration | nonradioactive representative salt; authorized fuel-salt confirmation as required | Q1-Q3 2028 | demonstrator processing equipment; operating procedures; commercial scale-up |
| CHEM-20 | Sampling representativeness and hot-sampling qualification | nonradioactive first; authorized fuel-salt confirmation | Q2 2027-Q2 2029 | chemistry program; MC&A; model validation; source term |
| CHEM-21 | Online sensor drift, fouling, and cross-calibration | nonradioactive and later authorized confirmation | Q3 2027-Q4 2029 | instrument specification; surveillance interval; alarm/action levels |
| CHEM-22 | Radiation-environment compatibility | non-fissile or surrogate materials; licensed irradiation/hot-cell work | 2028-2031 | source term; instrument qualification; off-gas media life; materials life |
| CHEM-23 | Irradiated-salt confirmatory characterization | irradiated fuel salt and deposits | Q4 2028-Q3 2029 | mechanistic source term; fission-product transport; MC&A; chemistry model validation |
| CHEM-24 | Demonstrator chemistry and processing performance | operating fuel salt | 2029 | commercial design and licensing; operating limits; processing system sizing; maintenance and waste |
| CHEM-25 | Processing waste and residual-salt characterization | nonradioactive and radioactive as generated | 2027-2038 | waste system design; DOE return/disposition; commercial decommissioning and lifecycle cost |

## Detailed experiment definitions

### CHEM-01 - Incoming salt/feed qualification

**Objective:** Verify supplier certificates and establish an independent baseline for carrier salt and fissile/feed precursor before synthesis or loop loading.

**Configuration:** Representative samples from each supplier lot and container; duplicate samples retained.

**Material progression:** nonradioactive carrier salt first; authorized fissile feed for production acceptance

**Facility strategy:** Qualified commercial or national-laboratory analytical laboratory

**Planned window:** Q4 2026-Q2 2027

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- starting impurity vector
- batch mass and mixing history
- purification/synthesis route identifier
- residual heel and recovery fraction

**Primary measurements**

- identity and composition
- moisture/oxygen and corrosion-active impurities
- metallic impurities
- particle/foreign material
- batch uniformity

**Analytical methods**

- ICP-MS/OES or equivalent
- ion chromatography or equivalent
- oxygen/moisture analysis
- XRD/Raman as applicable
- independent laboratory cross-check

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- batch preparation vessel and transfer system
- representative purification media/reagents selected by the approved process
- independent analytical laboratory

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

All required constituents and impurity limits meet the controlled procurement specification; any discrepancy is resolved before use.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-INL-05`

### CHEM-02 - Carrier-salt purification scale-up

**Objective:** Demonstrate the selected purification route from bench to engineering batch and quantify impurity removal, salt recovery, repeatability, and waste generation.

**Configuration:** Bench batches followed by an engineering-scale batch in the selected preparation system.

**Material progression:** nonradioactive carrier salt

**Facility strategy:** ORNL/INL or equivalent qualified molten-salt preparation facility

**Planned window:** Q1-Q4 2027

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- starting impurity vector
- batch mass and mixing history
- purification/synthesis route identifier
- residual heel and recovery fraction

**Primary measurements**

- before/after impurity concentrations
- salt mass recovery
- process time
- secondary waste quantity
- equipment fouling and cleanability

**Analytical methods**

- qualified chemical analysis
- mass balance
- process instrumentation
- repeat batches

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- batch preparation vessel and transfer system
- representative purification media/reagents selected by the approved process
- independent analytical laboratory

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Project impurity targets are met in repeated batches with closed mass balance, controlled waste, and no unacceptable equipment degradation.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-ITHF-18`
- `S-ITHF-28`

### CHEM-03 - Fuel-salt synthesis batch repeatability

**Objective:** Qualify the synthesis and blending route and demonstrate chemical/isotopic homogeneity and repeatability before production fuel.

**Configuration:** Sequential qualification batches using surrogate or authorized low-consequence feed, followed by the production-process qualification batch.

**Material progression:** surrogate/non-fissile, then authorized uranium-bearing qualification batch

**Facility strategy:** Authorized national-laboratory or licensed fuel-salt synthesis facility

**Planned window:** Q2 2027-Q2 2028

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- starting impurity vector
- batch mass and mixing history
- purification/synthesis route identifier
- residual heel and recovery fraction

**Primary measurements**

- composition and homogeneity
- material balance
- yield/recovery
- impurity pickup
- sampling variability
- off-specification disposition

**Analytical methods**

- multi-location sampling
- independent chemical and isotopic analysis
- mass-accountancy reconciliation

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- batch preparation vessel and transfer system
- representative purification media/reagents selected by the approved process
- independent analytical laboratory

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Repeated batches meet specification and sampling uncertainty is small enough to support acceptance and MC&A conclusions.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-INL-05`
- `D-DEMO-04`

### CHEM-04 - Phase and freeze-thaw behavior

**Objective:** Measure solidus/liquidus or transition behavior and identify segregation, precipitation, or remelting concerns across the operating composition envelope.

**Configuration:** Small sealed specimens spanning nominal composition, manufacturing tolerance, impurity, and burnup-surrogate states.

**Material progression:** nonradioactive and authorized uranium-bearing samples as needed

**Facility strategy:** Qualified chemistry/materials laboratory

**Planned window:** Q1 2027-Q4 2028

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- transition temperatures
- latent heat
- phase identification
- segregation after freeze/thaw
- repeat-cycle stability

**Analytical methods**

- DSC/DTA
- XRD
- microscopy
- controlled freeze-thaw cycles

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Measured behavior supports heat-trace, drain, recovery, sampling, and storage margins with quantified uncertainty.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-MSR-07`
- `S-ITHF-39`

### CHEM-05 - Thermophysical property matrix

**Objective:** Generate the density, viscosity, heat capacity, thermal conductivity, and vapor/volatility data required by system and accident models.

**Configuration:** Controlled composition and temperature matrix including nominal, tolerance, impurity, and selected fission-product-surrogate states.

**Material progression:** nonradioactive and authorized uranium-bearing specimens

**Facility strategy:** National-laboratory or qualified university/commercial property laboratory

**Planned window:** Q4 2026-Q2 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- density
- viscosity
- heat capacity
- thermal conductivity
- vapor pressure or volatility indicators
- measurement covariance

**Analytical methods**

- qualified property methods
- reference materials
- replicate measurements
- inter-laboratory comparison

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Correlations cover the approved analysis domain and meet the uncertainty targets in the methods plan; gaps are bounded and flagged.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-MSR-02`

### CHEM-06 - Redox sensor calibration and reference-electrode qualification

**Objective:** Select and calibrate the online/electrochemical redox measurement method and establish drift, fouling, and maintenance requirements.

**Configuration:** Controlled salt pots with known reference states and representative sensor materials/feedthroughs.

**Material progression:** nonradioactive salt; later authorized fuel salt confirmation

**Facility strategy:** Qualified high-temperature chemistry laboratory and ITHF

**Planned window:** Q1 2027-Q2 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- sensor serial number and calibration
- immersion/exposure history
- sampling probe geometry and purge history
- drift/fouling challenge
- laboratory cross-check timing

**Primary measurements**

- sensor response
- accuracy and repeatability
- temperature dependence
- drift
- response time
- fouling/cleaning

**Analytical methods**

- electrochemical measurement
- independent wet chemistry/spectroscopy
- reference standards

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- online sensor test rack
- hot sampling assembly
- reference-electrode or calibration system
- laboratory cross-check equipment

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Sensor uncertainty and drift remain within the chemistry control budget over the required maintenance interval.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-MSR-05`

### CHEM-07 - Impurity perturbation and recovery

**Objective:** Demonstrate detection and recovery from controlled oxygen/moisture or corrosion-product perturbations without damaging the loop or losing material accountability.

**Configuration:** Small salt pot and then representative loop with approved nonradioactive perturbations; no fissile separation operation.

**Material progression:** nonradioactive representative salt

**Facility strategy:** Non-nuclear salt loop with containment and cleanup capability

**Planned window:** Q2 2027-Q4 2028

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- online sensor response
- laboratory confirmation
- corrosion-product release
- purification/recovery time
- salt loss

**Analytical methods**

- online electrochemistry/spectroscopy
- chemical analysis
- mass balance
- coupon examination

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

The perturbation is detected, action limits trigger correctly, the approved recovery process restores the chemistry envelope, and resulting corrosion/waste remains acceptable.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-02`
- `S-MSR-04`
- `S-MSR-05`
- `S-ITHF-45`

### CHEM-08 - Static corrosion matrix

**Objective:** Establish alloy, weld, coating, and graphite/ceramic compatibility across temperature, redox, impurity, and surrogate-fission-product conditions.

**Configuration:** Sealed or controlled-atmosphere capsules with traceable material heats, weldments, and witness coupons.

**Material progression:** nonradioactive representative salt and surrogates

**Facility strategy:** Qualified materials laboratory

**Planned window:** Q4 2026-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- alloy heat and weld/joining pedigree
- surface finish and specimen geometry
- flow/thermal-gradient exposure
- pre/post exposure mass and dimensions

**Primary measurements**

- mass change
- attack depth
- elemental depletion
- mechanical property change
- deposit chemistry

**Analytical methods**

- gravimetry
- SEM/EDS
- XRD
- metallography
- mechanical testing

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- traceable coupons/weldments
- metallography and microscopy tools
- mechanical test and NDE capability

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Corrosion/degradation data support the design allowance and life model with reproducible trends and quantified scatter.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-02`
- `S-MTH-05`
- `S-MSR-09`

### CHEM-09 - Flow-assisted corrosion and mass transfer

**Objective:** Measure corrosion and deposition under representative flow, thermal gradients, and chemistry control, including hot-to-cold mass transfer.

**Configuration:** Forced-circulation loop with removable coupons/spools and controlled chemistry.

**Material progression:** nonradioactive representative salt

**Facility strategy:** ITHF or dedicated materials loop

**Planned window:** Q2 2027-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- alloy heat and weld/joining pedigree
- surface finish and specimen geometry
- flow/thermal-gradient exposure
- pre/post exposure mass and dimensions

**Primary measurements**

- corrosion rate and location
- mass transfer/deposition
- chemistry evolution
- pressure drop
- component fouling

**Analytical methods**

- loop sampling
- online chemistry
- coupon/spool examination
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- traceable coupons/weldments
- metallography and microscopy tools
- mechanical test and NDE capability

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Observed degradation and deposition remain within the design/inspection envelope and are predictable by the released model.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-02`
- `S-MSR-09`
- `S-ITHF-45`

### CHEM-10 - Weld, joint, seal, and heat-affected-zone qualification

**Objective:** Demonstrate that production joining and sealing details do not create localized chemistry, corrosion, leakage, or embrittlement weaknesses.

**Configuration:** Production-representative welds, brazes, seals, coatings, and dissimilar-material joints exposed in static and flow conditions.

**Material progression:** nonradioactive representative salt

**Facility strategy:** Qualified fabrication supplier and materials laboratory

**Planned window:** Q2 2027-Q4 2032

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- alloy heat and weld/joining pedigree
- surface finish and specimen geometry
- flow/thermal-gradient exposure
- pre/post exposure mass and dimensions

**Primary measurements**

- leak tightness
- localized attack
- mechanical properties
- NDE detectability
- repairability

**Analytical methods**

- pressure/leak testing
- NDE
- metallography
- mechanical testing

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- traceable coupons/weldments
- metallography and microscopy tools
- mechanical test and NDE capability

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Production details meet design, inspection, repair, and lifetime acceptance criteria after exposure.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-02`
- `S-MSR-09`
- `D-DEMO-03`
- `P-PKG-02`

### CHEM-11 - Fission-product surrogate solubility and speciation

**Objective:** Determine where representative soluble, semi-soluble, and precipitating fission-product groups reside as chemistry and temperature change.

**Configuration:** Salt pots with a controlled matrix of stable surrogates selected by chemical group; later compare with irradiated samples.

**Material progression:** stable nonradioactive surrogates first

**Facility strategy:** Qualified chemistry laboratory

**Planned window:** Q2 2027-Q2 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species group and concentration ladder
- redox condition
- precipitation/solubility boundary
- actinide-retention surrogate or authorized confirmatory measurement

**Primary measurements**

- dissolved concentration
- precipitation threshold
- species/oxidation state
- distribution between salt, gas, deposit, and filter

**Analytical methods**

- ICP-MS/OES
- spectroscopy
- electrochemistry
- solid phase characterization
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- surrogate dosing system
- phase/speciation analysis capability
- closed material-balance collection system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Group behavior and uncertainty are sufficient to parameterize source-term, plate-out, processing, and safeguards models.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MTH-04`
- `S-MSR-04`

### CHEM-12 - Noble-metal surrogate plate-out

**Objective:** Measure deposition locations, rates, resuspension, and decontamination behavior for representative noble-metal species.

**Configuration:** Thermal-gradient flow loop with removable coupons, filters, and controlled surface materials.

**Material progression:** stable surrogates

**Facility strategy:** Representative flow loop with removable test sections

**Planned window:** Q3 2027-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species injection history
- gas residence time and flow split
- surface-area and temperature map
- filter/sorbent identity and loading
- deposition and recovery locations

**Primary measurements**

- surface inventory
- bulk concentration
- deposition rate
- resuspension
- decontamination effectiveness

**Analytical methods**

- surface analysis
- bulk chemical analysis
- removable spool/coupon examination
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- gas injection and metering system
- representative off-gas train
- particle/aerosol and gas-species monitoring
- removable deposition coupons and recoverable filters/sorbents

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Mass balance closes within the project uncertainty target and the transport model predicts dominant deposition zones and inventories.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-MSR-04`
- `D-RD-01`
- `S-ITHF-45`

### CHEM-13 - Stable noble-gas stripping and residence time

**Objective:** Quantify gas transfer from salt to cover gas and the effects of flow, free surface, bubbles, and gas contactor design.

**Configuration:** Representative salt loop with stable noble gases and controlled cover-gas flow; no radioactive gas required for initial qualification.

**Material progression:** stable noble-gas tracers

**Facility strategy:** ITHF/off-gas analog loop

**Planned window:** Q2 2028-Q2 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- transfer coefficient
- residence time
- gas holdup
- carryover
- off-gas concentration response

**Analytical methods**

- mass-flow control
- gas chromatography or spectroscopy
- high-speed/void instrumentation as applicable

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Measured transfer and residence-time behavior validates the off-gas/source-term model over the intended operating range.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-MSR-04`
- `S-ITHF-40`

### CHEM-14 - Aerosol generation, transport, and capture

**Objective:** Measure aerosol formation, size distribution, deposition, and removal across demisters/filters under representative gas and salt conditions.

**Configuration:** Heated cover-gas test train with controlled salt aerosol or stable surrogate aerosol generation.

**Material progression:** nonradioactive surrogates

**Facility strategy:** Qualified off-gas test stand

**Planned window:** Q3 2027-Q3 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species injection history
- gas residence time and flow split
- surface-area and temperature map
- filter/sorbent identity and loading
- deposition and recovery locations

**Primary measurements**

- aerosol size and mass
- capture efficiency
- pressure drop
- re-entrainment
- sensor response

**Analytical methods**

- particle sizing
- filter gravimetry
- LIBS or equivalent spectroscopy
- surface sampling

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- gas injection and metering system
- representative off-gas train
- particle/aerosol and gas-species monitoring
- removable deposition coupons and recoverable filters/sorbents

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Treatment stages meet project removal and pressure-drop targets, and monitoring detects breakthrough within the required response time.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MSR-04`
- `S-MSR-05`

### CHEM-15 - Volatile-halogen surrogate capture

**Objective:** Down-select and qualify the capture sequence for volatile halogen species using nonradioactive surrogates before any radioactive confirmation.

**Configuration:** Bench columns followed by an integrated heated off-gas train with representative humidity, aerosol, and flow transients.

**Material progression:** stable surrogates

**Facility strategy:** Qualified off-gas laboratory

**Planned window:** Q3 2027-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species injection history
- gas residence time and flow split
- surface-area and temperature map
- filter/sorbent identity and loading
- deposition and recovery locations

**Primary measurements**

- breakthrough curve
- capacity
- decontamination factor
- temperature sensitivity
- regeneration/disposal behavior
- secondary waste

**Analytical methods**

- online spectroscopy
- sorbent analysis
- mass balance
- pressure-drop monitoring

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- gas injection and metering system
- representative off-gas train
- particle/aerosol and gas-species monitoring
- removable deposition coupons and recoverable filters/sorbents

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Selected media/train achieves the project-defined retention and monitoring performance with acceptable waste, heat, and replacement interval.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MSR-04`
- `D-3.9.f`
- `P-3.11.b`

### CHEM-16 - Alkali/cesium surrogate capture

**Objective:** Evaluate aerosol and vapor-phase capture of representative alkali species and identify deposition/fouling risks.

**Configuration:** Heated off-gas train with stable alkali surrogates and representative aerosols.

**Material progression:** stable surrogates

**Facility strategy:** Qualified off-gas laboratory

**Planned window:** Q4 2027-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species injection history
- gas residence time and flow split
- surface-area and temperature map
- filter/sorbent identity and loading
- deposition and recovery locations

**Primary measurements**

- capture efficiency
- breakthrough
- deposit location
- fouling
- sensor calibration

**Analytical methods**

- LIBS or equivalent
- filter/sorbent analysis
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- gas injection and metering system
- representative off-gas train
- particle/aerosol and gas-species monitoring
- removable deposition coupons and recoverable filters/sorbents

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

The selected train and monitoring method achieve the project retention and operability targets across representative transients.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MSR-04`
- `S-MSR-05`

### CHEM-17 - Particulate filtration and cleanup

**Objective:** Demonstrate removal of precipitates/corrosion products without unacceptable fuel/salt loss, plugging, or maintenance burden.

**Configuration:** Bench filters followed by a bypass cleanup skid with controlled surrogate particulates.

**Material progression:** nonradioactive salt and surrogates

**Facility strategy:** Representative salt cleanup skid

**Planned window:** Q2 2027-Q3 2028

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species injection history
- gas residence time and flow split
- surface-area and temperature map
- filter/sorbent identity and loading
- deposition and recovery locations

**Primary measurements**

- removal efficiency
- pressure drop
- salt hold-up
- filter life
- backflush/replacement behavior
- waste quantity

**Analytical methods**

- particle sizing
- differential pressure
- chemical analysis
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- gas injection and metering system
- representative off-gas train
- particle/aerosol and gas-species monitoring
- removable deposition coupons and recoverable filters/sorbents

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Selected filtration concept meets removal, pressure-drop, salt-recovery, maintainability, and waste targets.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `D-DEMO-04`
- `S-ITHF-18`

### CHEM-18 - Targeted rare-earth/lanthanide removal down-select

**Objective:** Determine whether targeted removal is technically and economically justified and screen candidate separation principles with stable surrogates.

**Configuration:** Small controlled batch tests comparing candidate physical/chemical/electrochemical separation principles; no production-scale fissile separation.

**Material progression:** stable nonradioactive surrogates; authorized uranium-bearing confirmation only if needed

**Facility strategy:** Qualified chemistry laboratory; radioactive confirmation only in an authorized facility

**Planned window:** Q2 2027-Q4 2027

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- surrogate species group and concentration ladder
- redox condition
- precipitation/solubility boundary
- actinide-retention surrogate or authorized confirmatory measurement

**Primary measurements**

- decontamination factor
- actinide/fuel retention
- salt recovery
- selectivity
- waste generation
- fouling
- cycle time
- safeguards measurement impact

**Analytical methods**

- chemical analysis
- mass balance
- equipment inspection
- process monitoring

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- surrogate dosing system
- phase/speciation analysis capability
- closed material-balance collection system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

A documented trade study selects no routine removal, off-gas-only, targeted removal, or broader processing based on safety, reactivity, corrosion, source term, safeguards, waste, operability, and lifecycle cost; any selected method meets project-defined recovery and retention criteria.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `S-MSR-04`
- `S-MSR-06`
- `P-OPT-06`

### CHEM-19 - Integrated salt-processing skid repeated-cycle demonstration

**Objective:** Demonstrate the selected minimal processing train as an integrated, maintainable system and quantify performance degradation over repeated cycles.

**Configuration:** Engineering-scale bypass skid including the selected purification, filtration, gas contact, sampling, and monitoring functions; separation scope limited to the approved architecture.

**Material progression:** nonradioactive representative salt; authorized fuel-salt confirmation as required

**Facility strategy:** Engineering-scale non-nuclear loop followed by authorized fuel-salt commissioning

**Planned window:** Q1-Q3 2028

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- mass balance closure
- salt/fuel retention
- removal/capture performance
- throughput
- availability
- sensor performance
- maintenance dose/work proxy
- waste and consumables

**Analytical methods**

- online instruments
- laboratory analysis
- mass/accountancy model
- inspection and maintenance records

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Repeated cycles meet performance, retention, mass-balance, maintainability, and waste targets without unacceptable accumulation or uncontrolled inventory transfer.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-RD-01`
- `D-DEMO-04`
- `S-MSR-06`
- `P-PKG-02`

### CHEM-20 - Sampling representativeness and hot-sampling qualification

**Objective:** Prove that routine and confirmatory samples represent the system inventory and can be obtained without contamination, plugging, excessive hold-up, or loss of accountability.

**Configuration:** Representative sampling points, lines, valves, sample containers, and freeze/thaw cycles under controlled flow and chemistry.

**Material progression:** nonradioactive first; authorized fuel-salt confirmation

**Facility strategy:** ITHF and authorized fuel-salt system

**Planned window:** Q2 2027-Q2 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- sensor serial number and calibration
- immersion/exposure history
- sampling probe geometry and purge history
- drift/fouling challenge
- laboratory cross-check timing

**Primary measurements**

- sample bias and variability
- hold-up
- cross-contamination
- plugging/freezing
- operator cycle time
- inventory reconciliation

**Analytical methods**

- paired samples
- online-versus-lab comparison
- tracer/mass balance
- repeatability study

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- online sensor test rack
- hot sampling assembly
- reference-electrode or calibration system
- laboratory cross-check equipment

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Sampling bias and repeatability meet the data/MC&A uncertainty budget and the procedure is executable under operating constraints.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-MSR-05`
- `S-MSR-06`
- `D-DEMO-04`
- `P-7.i`

### CHEM-21 - Online sensor drift, fouling, and cross-calibration

**Objective:** Establish calibration, drift, fouling, failure detection, maintenance, and replacement intervals for online chemistry/off-gas sensors.

**Configuration:** Long-duration salt and off-gas test with deliberate normal operating changes and removable sensors.

**Material progression:** nonradioactive and later authorized confirmation

**Facility strategy:** ITHF/off-gas test stand and qualified lab

**Planned window:** Q3 2027-Q4 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status
- sensor serial number and calibration
- immersion/exposure history
- sampling probe geometry and purge history
- drift/fouling challenge
- laboratory cross-check timing

**Primary measurements**

- accuracy
- drift
- response time
- fouling
- failure modes
- calibration recovery

**Analytical methods**

- online electrochemistry/spectroscopy
- laboratory reference analysis
- calibration checks

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- online sensor test rack
- hot sampling assembly
- reference-electrode or calibration system
- laboratory cross-check equipment

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Sensor performance remains within the approved uncertainty and detection budget over the maintenance interval or a validated compensation/maintenance method is defined.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-MSR-05`
- `S-ITHF-45`
- `P-7.i`

### CHEM-22 - Radiation-environment compatibility

**Objective:** Identify radiation-induced changes in salt chemistry, sensors, sorbents, seals, and sampling materials before relying on non-irradiated tests for reactor service.

**Configuration:** Gamma exposure and, where justified, irradiation capsule or irradiated-salt sample program with matched controls.

**Material progression:** non-fissile or surrogate materials; licensed irradiation/hot-cell work

**Facility strategy:** National-laboratory irradiation and hot-cell facilities

**Planned window:** 2028-2031

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- chemical/speciation change
- gas generation
- sensor drift
- sorbent capacity change
- material degradation

**Analytical methods**

- gamma facility
- post-exposure chemical/material analysis
- control specimens

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Radiation effects are bounded in the chemistry, off-gas, sensor, and materials models or qualified component limits are established.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-MTH-04`
- `S-MTH-05`
- `S-MSR-04`
- `S-MSR-05`

### CHEM-23 - Irradiated-salt confirmatory characterization

**Objective:** Confirm surrogate-based speciation, partitioning, source-term, corrosion, and mass-accountancy models with samples from the INL critical experiment.

**Configuration:** Controlled samples and deposits from defined experiment states, analyzed in hot cells with matched pre-irradiation baselines.

**Material progression:** irradiated fuel salt and deposits

**Facility strategy:** INL or equivalent authorized hot-cell facility

**Planned window:** Q4 2028-Q3 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Confirm the DOE/host authorization, radiological work package, material-control boundaries, hot-cell/sample-transfer route, dose/contamination controls, and approved waste/end-state disposition before the activity begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- isotopic/elemental inventory
- speciation indicators
- gas/salt/deposit partitioning
- corrosion products
- sample and inventory reconciliation

**Analytical methods**

- hot-cell sample preparation
- radiochemical analysis
- spectroscopy/microscopy
- mass-accountancy reconciliation

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- authorized hot-cell or shielded analytical capability
- radiological survey and contamination-control equipment
- MC&A-compatible sample and residue tracking

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Results are traceable to operating history and close or bound the key surrogate-to-radioactive extrapolations needed for demonstrator/commercial design use.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `S-INL-19`
- `S-MSR-04`
- `S-MSR-06`
- `S-MTH-04`

### CHEM-24 - Demonstrator chemistry and processing performance

**Objective:** Validate chemistry control, sampling, off-gas/cleanup performance, inventory tracking, and operating procedures under coupled nuclear and thermal conditions.

**Configuration:** Approved demonstrator operating campaigns with staged power/chemistry conditions and predefined hold points.

**Material progression:** operating fuel salt

**Facility strategy:** DOE-authorized demonstrator and qualified laboratories

**Planned window:** 2029

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Confirm the DOE/host authorization, radiological work package, material-control boundaries, hot-cell/sample-transfer route, dose/contamination controls, and approved waste/end-state disposition before the activity begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- chemistry trends and action-level response
- gas/salt/deposit inventory
- processing performance
- corrosion/sensor trends
- mass balance
- waste and consumables

**Analytical methods**

- online sensors
- laboratory samples
- off-gas monitoring
- inventory/accountancy model
- post-operation examination

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system
- authorized hot-cell or shielded analytical capability
- radiological survey and contamination-control equipment
- MC&A-compatible sample and residue tracking

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

The integrated system remains within chemistry and material limits; measured partitioning and processing performance support the commercial safety case and operating program with quantified uncertainty.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-EXP-09`
- `D-EXP-10`
- `D-EXP-12`
- `D-EXP-14`
- `P-OPT-04`
- `P-OPT-06`

### CHEM-25 - Processing waste and residual-salt characterization

**Objective:** Characterize every filter, sorbent, residue, sample, heel, contaminated component, and secondary waste stream created by chemistry and processing operations.

**Configuration:** Representative waste generated by bench, engineering-scale, critical-experiment, and demonstrator campaigns.

**Material progression:** nonradioactive and radioactive as generated

**Facility strategy:** Qualified waste laboratory and authorized storage/disposition organizations

**Planned window:** 2027-2038

**Minimum execution sequence**

1. Approve the test objective, decision supported, configuration, material stage, measured quantities, uncertainty target, sample plan, and acceptance basis.
2. Verify material identity/genealogy, equipment configuration, calibrations, cleanliness, atmospheric controls, hazards, and waste/disposition route before work begins.
3. Execute a pre-test prediction or expected-response calculation and freeze the prediction before the measured result is released to the analysis team.
4. Run the planned sequence with time-synchronized process data, operator log, configuration changes, sample custody, and exception records.
5. Perform replicate or confirmatory measurements, calculate uncertainty and material balance, reconcile laboratory and online measurements, and document outliers.
6. Independently review the qualified dataset, compare it to acceptance criteria and model predictions, disposition discrepancies, and release the data with conditions of use.

**Controlled variables**

- salt composition and supplier lot
- temperature history and thermal cycling
- cover-gas composition/flow where applicable
- contact material and exposed surface condition
- sampling time/location and analytical method
- equipment configuration and calibration status

**Primary measurements**

- chemical and radionuclide inventory
- physical form
- leachability/stability as applicable
- heat/dose
- packaging compatibility
- material-accountability closure

**Analytical methods**

- qualified chemical/radiochemical analysis
- dose/heat calculation
- waste acceptance testing
- mass balance

**Equipment and consumables**

- qualified salt preparation/transfer equipment
- controlled-atmosphere enclosure or cover-gas system
- calibrated temperature, mass, flow, pressure, and electrochemical instruments
- qualified sample containers and chain-of-custody materials
- approved analytical laboratory methods and reference standards
- time-synchronized data-acquisition and records system

**Replication and uncertainty:** Use at least duplicate independently analyzed samples for acceptance-critical chemistry, repeat the condition after configuration stabilization, include blanks/reference materials where applicable, and define the uncertainty budget before test execution. Any reduction in replication requires a documented technical basis and independent approval.

**Sample and archive plan:** Assign a unique genealogy to feed, intermediate, product, deposits, filters/sorbents, residues, and retained reference samples. Record time/location/configuration, preserve sufficient archive material for dispute resolution and method reanalysis, and reconcile all samples to the campaign material balance.

**Stop conditions**

- loss of required atmosphere, temperature, containment, or criticality/material-control boundary
- instrument/calibration condition outside the approved range
- uncontrolled composition change, leak, plugging, precipitation, or unexpected pressure/flow response
- material balance discrepancy or sample-custody break that could invalidate the conclusion
- result outside a safety, authorization, equipment-protection, or preapproved test-abort limit

**Acceptance basis**

Each stream has an approved characterization, classification, packaging, storage, transport, treatment, and final disposition path before routine processing begins.

**Decision rule:** Credit the result only when the approved configuration was maintained, measurement uncertainty supports the required discrimination, material/sample balance is reconciled, independent review is complete, and the result is within acceptance or has an approved model/design/process update and retest disposition.

**Data products**

- controlled test procedure and readiness record
- as-tested configuration and material genealogy
- raw time-series and laboratory data in native format
- calibration and uncertainty records
- sample/deposit/filter inventory and material balance
- qualified dataset and comparison to prediction
- discrepancy dispositions and approved data-release memo

**Linked WBS activities**

- `D-DEMO-09`
- `P-3.11.g`
- `P-OPT-06`

## Cost treatment

The experiment matrix is an execution breakdown of existing chemistry, materials, methods, ITHF, INL, demonstrator, and commercial qualification tasks. Do not add its rows to the program total a second time.

## Official source and precedent links

- https://www.ornl.gov/project/liquid-salt-test-loop
- https://www.ornl.gov/group/esd/projects
- https://www.ornl.gov/publication/engineering-scale-batch-purification-ternary-mgcl2-kcl-nacl-salt-using-thermal-and
- https://www.ornl.gov/publication/redox-potential-control-molten-salt-systems-corrosion-mitigation
- https://www.ornl.gov/publication/monitoring-noble-gases-xe-and-kr-and-aerosols-cs-and-rb-molten-salt-reactor-surrogate
- https://www.ornl.gov/publication/monitoring-xenon-capture-metal-organic-framework-using-laser-induced-breakdown
- https://www.ornl.gov/publication/impact-europium-fission-product-surrogate-chromium-corrosion-molten-chloride-salt
- https://www.ornl.gov/publication/dynamic-mass-accountancy-modeling-molten-salt-reactor-using-equilibrium-thermodynamics
- https://www.osti.gov/biblio/4077644
