# Optional evidence separation (T10 L1)

Set `DAALE_EVIDENCE_SEPARATION=true` to enable L1 prompt construction for the
CLI, live-check helper, and HTTP service. The default is `false`.

When enabled, the prompt:

1. Serializes case metadata, policy, and prior kernel outputs before the
   evidence block.
2. Keeps the supplied evidence objects unchanged and places them between a
   deterministic boundary token derived from the complete case content. The
   token is checked against the evidence text and deterministically adjusted
   if it is already present.
3. Repeats the kernel's complete task instructions after the closing boundary,
   followed by the existing relation-matrix and output-schema instructions.

When disabled, prompt construction follows the prior code path and produces
the existing message layout. This flag changes only prompt construction; it
does not alter validation, synthesis, policy rules, or decision authority.

This is a separation measure, not a prompt-injection prevention guarantee.
Documents remain untrusted model input and can still influence a model despite
the delimiters. The effect requires a live, quota-approved A/B evaluation
before making any claim about improved resistance. No such evaluation is run
by offline construction tests.
