#!/usr/bin/env python3
"""Fail closed if the explicitly named research dataset is not private."""
import sys
from kaggle.api.kaggle_api_extended import KaggleApi,ApiGetDatasetRequest
owner,slug=sys.argv[1].split('/',1)
api=KaggleApi();api.authenticate()
with api.build_kaggle_client() as client:
    req=ApiGetDatasetRequest();req.owner_slug=owner;req.dataset_slug=slug
    dataset=client.datasets.dataset_api_client.get_dataset(req)
    if dataset.is_private is not True: raise RuntimeError('Refusing to use a dataset that is not private')
print('Verified private dataset before submitting kernel.',flush=True)
