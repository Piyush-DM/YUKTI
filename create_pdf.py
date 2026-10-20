from fpdf import FPDF

content = """# Implementation Over Legacy Systems

**Status:** Research Artifact

## Purpose

This document defines how an institution adopts CHOIR while preserving the integrity of its historical record.

The objective is not to reconstruct unknowable past reasoning.

The objective is to establish truthful institutional memory from the moment constitutional observability begins.

## Cause

During architecture development, a succession scenario exposed a critical limitation.

A high-ranking executive leaves.

The replacement inherits documents but not the predecessor's internal reasoning.

An obvious solution appeared: recover historical reasoning from legacy systems.

That approach was rejected.

Hidden human reasoning and hidden model reasoning cannot be truthfully reconstructed from documents or conversations alone.

This document records the constitutional alternative.

## Core Principle

> The institution shall preserve only what it can represent truthfully.

Where provenance cannot be preserved, the institution preserves the material rather than inventing the reasoning.

This becomes the boundary between legacy systems and constitutional memory.

## The Adoption Event

An institution does not become constitutional retroactively.

It becomes constitutional at a single observable transition.

This transition is called the **Adoption Event**.

Example:

Institution: Northstar Capital

Adoption Event:
2028-04-12

Before:
Legacy Material

After:
Institutional Memory

The Adoption Event is irreversible.

It marks the point from which institutional memory becomes constitutionally trustworthy.

## Legacy Material Classification

Legacy material enters the institution in three distinct classes.

| Legacy Material               | Constitutional Treatment             |
| ----------------------------- | ------------------------------------ |
| Documents                     | Preserve as Material                 |
| Explicit historical decisions | Preserve as Historical Artifacts     |
| Hidden reasoning              | Preserve absence; do not reconstruct |

The absence of recoverable reasoning is itself truthful information.

## Constitutional Boundary

Legacy material does not automatically become institutional memory.

Instead, legacy material becomes available as source material for future institutional reasoning.

Future judgments may reference legacy material.

They may not claim legacy reasoning that cannot be represented.

## Example

A company imports:

* Investment memos
* Board decks
* Meeting transcripts

These become Material.

The first reasoning session performed under constitutional observability becomes the institution's first canonical judgment.

The institution is not claiming that no previous decisions existed.

It is claiming that this is the first judgment whose provenance it can constitutionally guarantee.

## Relationship to the General Reasoning Baseline

The General Reasoning Baseline describes how a capable LLM externalizes working state.

This document describes how a real institution crosses from legacy systems into constitutional memory.

The two documents serve different purposes.

* GRB establishes the control group for reasoning behavior.
* Implementation Over Legacy Systems establishes the constitutional bridge for institutional adoption.

## Research Use

This document exists to define the transition between legacy environments and constitutional operation.

Future CHOIR development may refine implementation strategies.

The constitutional boundary remains unchanged:

The institution begins remembering at the moment it becomes capable of remembering truthfully."""

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Implementation Over Legacy Systems', new_x="LMARGIN", new_y="NEXT", align='C')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', new_x="RIGHT", new_y="TOP", align='C')

pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font('Helvetica', '', 11)
pdf.set_auto_page_break(auto=True, margin=20)

lines = content.split('\n')
for line in lines:
    pdf.set_x(10)
    if line.startswith('# '):
        pdf.set_font('Helvetica', 'B', 16)
        pdf.multi_cell(190, 10, line[2:])
        pdf.ln(3)
    elif line.startswith('## '):
        pdf.set_font('Helvetica', 'B', 14)
        pdf.multi_cell(190, 8, line[3:])
        pdf.ln(2)
    elif line.startswith('### '):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.multi_cell(190, 7, line[4:])
        pdf.ln(1)
    elif line.startswith('> '):
        pdf.set_font('Helvetica', 'I', 11)
        pdf.multi_cell(190, 7, line[2:])
        pdf.ln(2)
    elif line.startswith('* ') or line.startswith('- '):
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(190, 7, '- ' + line[2:])
    elif line.startswith('|'):
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(190, 6, line)
    elif line.strip() == '':
        pdf.ln(4)
    elif line.startswith('**') and line.endswith('**'):
        pdf.set_font('Helvetica', 'B', 11)
        pdf.multi_cell(190, 7, line.strip('*'))
    else:
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(190, 6, line)

pdf.output('choir/research/implementation_over_legacy_systems.pdf')
print("PDF created successfully")
