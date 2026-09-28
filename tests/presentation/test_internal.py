from httpx import AsyncClient


async def _create_ad(client: AsyncClient, auth_headers: dict[str, str]) -> dict:
    resp = await client.post(
        "/ads",
        headers=auth_headers,
        json={
            "title": "T",
            "description": "d",
            "price": 100,
            "category": "c",
            "city": "x",
        },
    )
    assert resp.status_code == 201
    return resp.json()


async def test_internal_get_returns_active(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.get(f"/internal/ads/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created["id"]
    assert data["status"] == "active"


async def test_internal_get_returns_archived(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    del_resp = await client.delete(f"/ads/{created['id']}", headers=auth_headers)
    assert del_resp.status_code == 204

    resp = await client.get(f"/internal/ads/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created["id"]
    assert data["status"] == "archived"


async def test_internal_get_not_found(client: AsyncClient) -> None:
    resp = await client.get("/internal/ads/999")
    assert resp.status_code == 404


async def test_internal_get_requires_no_auth(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await _create_ad(client, auth_headers)

    resp = await client.get(f"/internal/ads/{created['id']}")
    assert resp.status_code == 200
