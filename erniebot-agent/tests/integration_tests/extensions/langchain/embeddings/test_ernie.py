"""Test ERNIE embeddings."""
import time

import pytest
from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings


def test_ernie_embed_query() -> None:
    time.sleep(1)
    query = "foo"
    embedding = ErnieEmbeddings()
    output = embedding.embed_query(query)
    assert len(output) == 384


@pytest.mark.asyncio
async def test_ernie_aquery() -> None:
    time.sleep(1)
    query = "foo"
    embedding = ErnieEmbeddings()
    output = await embedding.aembed_query(query)
    assert len(output) == 384


def test_ernie_embed_documents() -> None:
    time.sleep(1)
    documents = ["foo", "bar"]
    embedding = ErnieEmbeddings()
    output = embedding.embed_documents(documents)
    assert len(output) == 2
    assert len(output[0]) == 384
    assert len(output[1]) == 384


@pytest.mark.asyncio
async def test_ernie_aembed_documents() -> None:
    time.sleep(1)
    documents = ["foo", "bar"]
    embedding = ErnieEmbeddings()
    output = await embedding.aembed_documents(documents)
    assert len(output) == 2
    assert len(output[0]) == 384
    assert len(output[1]) == 384
