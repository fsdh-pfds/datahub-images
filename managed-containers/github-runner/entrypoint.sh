#!/bin/sh -l

# Write the PEM key from the environment variable APP_KEY to a temporary file
temp_key=$(mktemp)
echo "$APP_KEY" > "$temp_key"

base64url() {
  openssl enc -base64 -A | tr '+/' '-_' | tr -d '='
}
sign() {
  openssl dgst -binary -sha256 -sign "$temp_key"
}

header="$(printf '{"alg":"RS256","typ":"JWT"}' | base64url)"
now="$(date '+%s')"
iat="$((now - 60))"
exp="$((now + (3 * 60)))"
template='{"iss":"%s","iat":%s,"exp":%s}'
payload="$(printf "$template" "$GITHUB_APP_ID" "$iat" "$exp" | base64url)"
signature="$(printf '%s' "$header.$payload" | sign | base64url)"
jwt="$header.$payload.$signature"

echo "header is: $header"
echo "payload is: $payload"
echo "signature is: $signature"
echo "jwt is: $jwt"
echo "APP_KEY content is:"
echo "$APP_KEY"

token="$(curl --location --silent --request POST \
  --url "https://api.github.com/app/installations/$INSTALLATION_ID/access_tokens" \
  --header "Accept: application/vnd.github+json" \
  --header "X-GitHub-Api-Version: 2022-11-28" \
  --header "Authorization: Bearer $jwt" \
  | jq -r '.token'
)"

echo "token is: $token"

registration_token="$(curl -X POST -fsSL \
  -H 'Accept: application/vnd.github.v3+json' \
  -H "Authorization: Bearer $token" \
  -H 'X-GitHub-Api-Version: 2022-11-28' \
  "$REGISTRATION_TOKEN_API_URL" \
  | jq -r '.token')"

echo "registration_token is: $registration_token"

./config.sh --url $GH_URL --token $registration_token --unattended --ephemeral && ./run.sh

# Clean up the temporary PEM file
rm "$temp_key"
