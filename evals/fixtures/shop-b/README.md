# Counter service

Staff produce receipts at a counter and from a nightly batch. Prices and receipts
are integer cents. TAX_BPS is the tax rate in basis points (1000 means 10%).
Both entry points should charge the same amount for the same basket and tax rate.
Receipts stay on this machine. Receipt history is required for customer disputes.

Run `python -m unittest discover -v` in a copy of this directory.
