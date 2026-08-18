# Project-MSR Planner 4.3.0 release notes

Release date: 2026-08-18

## Purpose

Version 4.3 is the execution-detail release. It preserves the v4.2 task-by-task cost baseline and schedule while adding a practical implementation plan to every WBS activity.

## Principal additions

- Added an implementation plan to all 937 activities.
- Added 11 cross-cutting execution playbooks.
- Added a six-phase fuel-supply plan covering requirements, DOE HALEU allocation, commercial backup, enrichment/deconversion, synthesis/analysis, packaging/transport/receipt and disposition.
- Added a 25-experiment chemistry/processing matrix covering feed, purification, synthesis, properties, redox, corrosion, fission-product surrogates, plate-out, off-gas, capture, sampling, sensors, integrated processing, irradiated confirmation, demonstrator operation and waste.
- Added bespoke execution sequences to 21 high-consequence work packages: chemistry methods/topical, thermophysical properties, mechanistic source term, online instrumentation and sampling, liquid-fuel MC&A, materials/corrosion/irradiation, fuel sourcing and receipt, INL data qualification, demonstrator chemistry/source-term/materials campaigns, commercial fuel scale-up, and post-startup fuel/salt/waste optimization.
- Added an **Implementation** section to the Streamlit application and an Implementation tab to every task inspector, including readable experiment sequences, controlled variables, equipment, replication, samples, stop conditions, data products and decision rules.
- Added implementation registers to scenario exports and made the full Excel workbook an on-demand export.
- Added an eight-item implementation closure register and a 937-row implementation audit.
- Preserved the password gate and plain uncompressed JSON sharding.

## Cost treatment

The new playbooks and experiment rows are non-additive execution crosswalks into the existing costed tasks. The nominal Launch Pad USA plus Part 53 COL total remains approximately $1,222.8 million. Quotations, DOE/host agreements, fuel allocation terms, laboratory work orders and capacity reservations should replace planning allowances in the next cost baseline.

## Verification

Schema and integrity validation passed; 52 automated tests passed; all 13 application sections passed control-flow smoke testing; all data shards remain below GitHub's file limit.
