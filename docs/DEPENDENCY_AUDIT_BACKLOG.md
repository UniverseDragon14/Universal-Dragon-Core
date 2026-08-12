# Dependency and Bundle Audit Backlog

Observed during Dragon Room Magic V1 validation on 2026-08-12.

## Dependency warning

`npm ci` completes successfully but reports:

```text
16 vulnerabilities (2 low, 5 moderate, 9 high)
```

No automatic `npm audit fix` is applied in the Room Magic feature branch. Dependency changes can alter runtime behavior and must be audited package-by-package with tests before upgrade.

## Bundle warning

The production Vite build succeeds but reports a main JavaScript asset of roughly 764 kB minified and warns about chunks larger than 500 kB.

A later performance pass should inspect route/component boundaries and use measured code splitting where it materially improves mobile startup without breaking the NOVA dashboard.

## Process rule

Do not mix broad dependency upgrades or bundle restructuring into a hardware/voice vertical-slice PR. Handle each as a scoped change with its own evidence and rollback path.
