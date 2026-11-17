"""The YUKTI engine's HTTP API: authenticated, per-client, persisted.

    portal  --HTTPS + client key-->  service  -->  R-Fabric pipeline  -->  model provider

The portal never talks to the model provider and never holds its key. Each
client organisation gets its own keys; the service stores only a hash of each.
"""
