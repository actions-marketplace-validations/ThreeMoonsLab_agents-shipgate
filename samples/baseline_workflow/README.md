# Baseline Workflow Sample

Use the support-refund fixture to create and apply a local baseline:

```bash
agents-shipgate baseline save \
  --config ../support_refund_agent/shipgate.yaml \
  --out .agents-shipgate/baseline.json

agents-shipgate scan \
  --config ../support_refund_agent/shipgate.yaml \
  --baseline .agents-shipgate/baseline.json \
  --ci-mode strict
```

The second command exits `0` because all active findings match the saved
baseline. If a new unsuppressed critical finding appears later, strict mode exits
`20`.
