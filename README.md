# Dead-Docs to Live-Code Verifier

An automated GitHub Action that uses Python AST and Meta-Llama-3.1-8B to detect outdated README code snippets.

## Quick Start
Use generate_invoice to calculate your bill total:

```python
from src.billing import generate_invoice

# Outdated snippet: uses removed 'discount' parameter and misses 'tax_rate'
invoice = generate_invoice(amount=500, discount=10)
print(invoice)
```
