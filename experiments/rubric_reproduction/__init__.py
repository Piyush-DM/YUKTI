"""Experiment: can a single LLM, given YUKTI's own investment reasoning rubric,
reproduce the frozen ``choir_prototype`` pipeline's output on a synthetic packet?

This package derives ground truth from the frozen implementation, transcribes the
rubric the deterministic kernels encode, and assembles the L-lo control prompt.
It makes **no** model call. See ``README.md``.
"""
