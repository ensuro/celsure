async function pricePolicy(model, expiration) {
  const response = await fetch(
    "/price_policy/?" + new URLSearchParams({ model, expiration }),
    {
      method: "get",
    }
  );
  return response.json();
}
