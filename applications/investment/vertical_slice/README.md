# Vertical Slice

The first complete end-to-end execution path in YUKTI. One fixed sample document
travels the whole pipeline and every stage writes its output to disk.

This is a **plumbing** slice. It proves the path exists and is inspectable at
every point. It does not add reasoning, and it is not a claim about experimental
objective O1 — the input is a constructed sample, not real case material.

## Run it

```powershell
python -m applications.investment.vertical_slice
```

No install, no configuration, no network, no API keys. Artifacts land in
`reports/vertical-slice/orbital-series-b/`. Add `--quiet` to write the artifacts
without printing the report.

## The path

```text
documents/orbital-series-b.json
      |
      v  parse.py                     -- deserialise + validate. No reasoning.
InvestmentPacket
      |
      v  domains/investment/translator.py
CHOIR IR
      |
      v  core/runtime.py              -- four independent kernels
Structured Artifacts
      |
      v  core/synthesizer.py
Institutional Recommendation
      |
      v  core/report.py               -- projection of the record
Execution Report
```

**Only the first arrow is new.** Everything from `InvestmentPacket` onward is
`choir_prototype/` called as a library and not modified in any way. That package
is frozen and hash-pinned; `python -m choir_prototype --frozen` still reports
INTACT with this slice in the tree, and `--audit` still reports portability 1.00.

## The artifacts

Every stage is persisted so it can be read on its own, without re-running
anything and without taking the final report's word for what happened.

| File | Stage |
|---|---|
| `01-document.json` | the document, as supplied — copied verbatim, not re-serialised |
| `02-packet.json` | what parsing produced |
| `03-ir.json` | the CHOIR intermediate representation |
| `04-artifacts.json` | what each kernel concluded, independently |
| `05-record.json` | the canonical record: `ir`, `artifacts`, `synthesis`, `trace` |
| `06-report.txt` | the rendered report |
| `metadata.json` | digests for the record, the report, and every file above |

`06-report.txt` is `.txt` rather than `.md` deliberately. It is the exact output
of `choir_prototype.core.report.render`, byte for byte. Reformatting it as
Markdown would make the renderer stop being a pure projection of the record,
which is the one property the report has that makes it worth reading.

`metadata.json` lists two kinds of hash and they are not interchangeable.
`record_digest` is the prototype's own hash over the structured record, taken
over the compact serialisation; the per-file `sha256` values are hashes of the
indented files as written. Both are recorded so neither has to be guessed at.

## What parsing is allowed to do

Map shapes. That is the whole permission.

The document format is the deal packet serialised — it is not prose, and there
is no extraction step. `parse.py` raises only *structural* errors: a missing
key, a wrong JSON type, a field that is not a string. It does not validate
vocabulary, so a `kind` or `status` the translator does not recognise falls
through to the translator's own conservative defaults rather than being rejected
at intake. That mapping is the translator's decision, and a second copy of it
here would be a second place to change it.

The reason for this discipline, and the options rejected, are in
[`DECISION-002`](../../../docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md).
It is **pending architect approval**.

The guarantee is mechanical rather than asserted. The sample document is the
frozen `ORBITAL_SERIES_B` packet serialised, so
`test_parsing_introduces_no_semantics` checks that the parsed packet is *equal*
to the packet inside the prototype. If intake ever starts interpreting,
defaulting, or normalising, that test fails before any downstream result has a
chance to look plausible.

## Determinism

The pipeline is deterministic by construction. This package adds the file I/O
the prototype deliberately refuses to do, and keeps the property: no timestamp,
no host detail, no run counter, output directory named by packet id, JSON keys
sorted, LF newlines on every platform.

Running the slice twice over the same document overwrites the artifacts with
identical bytes. `TestSliceDeterminism` checks exactly that, byte for byte,
rather than checking that the digests happen to agree.

## Scope

Deliberately one path, following the prototype's own standard for stated
omissions:

- **One document, named in `parse.py`.** Not a search path and not a registry —
  a registry would be an abstraction with one user.
- **One domain**, bound directly to `investment.DOMAIN`. There is no dispatch.
- **One format.** No format detection, no document-type support, no conversion.
- **No UI, no service, no persistence layer, no configuration system.**

## Tests

```powershell
python -m unittest discover -s applications/investment/vertical_slice -t .
```

17 tests, each naming the claim it defends. They write to a temporary directory
rather than `reports/`, so running the suite leaves nothing behind and does not
overwrite a run someone is reading.
