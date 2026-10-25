# Public-source research record

Checked on **2026-10-24 UTC** using ordinary HTTPS GET requests with certificate validation. This record distinguishes fetched documentation from blocked pages and from requirements supplied by the project brief. No account credentials, private endpoints, platform access controls, or copyrighted gameplay downloads were used. No competitor executable or proprietary source was inspected.

## Verified official Twitch documentation

The official API reference returned HTTP 200. Its HTML snapshot, held only in temporary research storage, had SHA-256 `97c53fe0a9c31334d322e2e93b55866d5b483ae45963fca4a7cbae359e33ee30`. A changing documentation site may produce a different hash later. Documentation availability is evidence of the API contract; it does not verify a live account integration.

| Source | URL | Verified information |
| --- | --- | --- |
| T1 | https://dev.twitch.tv/docs/api/reference/#create-clip-from-vod | VOD clip endpoint, parameters, permission requirements, response fields |
| T2 | https://dev.twitch.tv/docs/api/reference/#create-clip | Live clip endpoint, asynchronous completion, editing window |
| T3 | https://dev.twitch.tv/docs/api/reference/#get-clips | Clip URLs, nullable VOD association, query limits |
| T4 | https://dev.twitch.tv/docs/api/reference/#get-videos | Published VOD metadata and archive `stream_id` |
| T5 | https://dev.twitch.tv/docs/api/reference/#get-streams | Stream ID, category, broadcast start time |
| T6 | https://dev.twitch.tv/docs/api/guide/#twitch-rate-limits | Token buckets, rate headers, HTTP 429 behavior |
| T7 | https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#device-code-grant-flow | Device authorization flow and public-client requirements |
| T8 | https://dev.twitch.tv/docs/authentication/validate-tokens/ | Validation on startup and hourly thereafter |
| T9 | https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage | Authorized `channel.chat.message` viewer participation |
| T10 | https://dev.twitch.tv/docs/api/clips/ | Clip retrieval and unavailable/delayed VOD offsets |

### Create Clip From VOD

T1 describes `POST https://api.twitch.tv/helix/videos/clips`, creating a clip on behalf of the broadcaster or an editor. **Parameters are query parameters**, not a JSON request body.

| Parameter | Type | Required | Meaning |
| --- | --- | --- | --- |
| `editor_id` | string | yes | Editor ID; use the broadcaster ID when using the broadcaster's authorization; must match the user ID in the user access token |
| `broadcaster_id` | string | yes | Channel owner ID |
| `vod_id` | string | yes | Actual source VOD identifier |
| `vod_offset` | integer | yes | VOD-relative **end** of the clip, in seconds |
| `duration` | float | no | 5–60 seconds inclusive, precision 0.1, default 30 |
| `title` | string | yes | Clip title, subject to AutoMod |

`clip_start = vod_offset - duration`; `vod_offset` must be at least `duration`. This differs from the **start** offset returned by Get Clips.

The source's example, with credentials replaced by placeholders:

```sh
curl -X POST 'https://api.twitch.tv/helix/videos/clips?broadcaster_id=141981764&editor_id=12826&vod_id=2277656159&vod_offset=434&title=Standard%20Output' \
  -H 'Authorization: Bearer <user-access-token>' \
  -H 'Client-Id: <registered-client-id>'
```

HTTP 202 starts processing. The documented response is:

```json
{"data":[{"id":"FiveWordsForClipSlug","edit_url":"https://www.twitch.tv/twitchdev/clip/FiveWordsForClipSlug"}]}
```

These values are **official documentation examples**, not created clips. The response contains an ID and an editing URL; obtain the published viewer URL from Get Clips. Never fabricate a working viewer URL or treat request acceptance as completed publication.

Authorization lists `editor:manage:clips` or `channel:manage:clips`. The introductory authorization sentence mentions app or user tokens, while the parameter requirements and 401 table explicitly refer to a user token and matching `editor_id`. Use an authorized user token for this desktop workflow and verify the granted scopes and identity; this research does not establish an app-token-only flow. The 403 table includes unauthorized editors, disabled clips, follower/subscriber restrictions, and banned or timed-out users. The 404 table includes missing VOD, broadcaster, or editor.

The 404 table also repeats a requirement that the broadcaster be live, despite the endpoint's explicit description of clipping a VOD and earlier parts of an ongoing stream. This is a documentation inconsistency, not evidence that past VOD clipping requires a current live broadcast. Preserve the actual error response and provide a timestamp-link fallback when native creation is unavailable.

### Live Create Clip and Get Clips

T2 documents `POST /helix/clips` with a user token and `clips:edit`. It captures up to about 90 seconds around the API call; the published clip defaults to up to the final 30 seconds. The current reference lists optional query `title` and `duration` (5–60 inclusive, precision 0.1). Editing permits a 5–60 second selection; `edit_url` expires after 24 hours or publication, whichever comes first. The broadcaster must be live and permit clipping. This cannot be used as a general historical VOD clip selector.

Live clip creation is asynchronous: T2 advises checking Get Clips using the returned ID and treating no result after 60 seconds as failure. The VOD-specific section documents 202 but does not explicitly promise the same completion interval. A VOD integration should retain pending state and use bounded retrieval/retry rather than claim a documented VOD completion SLA.

T3 documents `GET /helix/clips`, accepting an app or user token. Specify exactly one of `id`, `broadcaster_id`, or `game_id`. Up to 100 IDs are permitted; `first` is 1–100 (default 20). Broadcaster/game results are sorted by descending views, and pagination yields approximately 1,000 results maximum unless queries are partitioned by date.

Relevant returned field types:

| Field | Type | Meaning / unavailable case |
| --- | --- | --- |
| `id` | string | Created clip identifier |
| `url` | string | Public viewer URL returned by Twitch |
| `embed_url` | string | Clip embed URL |
| `video_id` | string | Source VOD ID, or empty when unavailable |
| `vod_offset` | integer or null | VOD-relative **start** in seconds; null while association is pending or unavailable |
| `duration` | float | Seconds, precision 0.1 |
| `created_at` | string | RFC3339 creation time |
| `view_count` | integer | Views at retrieval, not a causal editing-quality measure |
| `title` | string | Title; does not establish factual event classification |

Offset association can be delayed by an indeterminate period, typically minutes. A deleted VOD may leave the clip available with an empty `video_id` and null `vod_offset`. Do not coerce null into zero or construct a VOD link using an unrelated ID.

### Stream/VOD identity and timeline mapping

T4 defines video `stream_id` as the stream from which an `archive` video originated; it is null for other video types. Correlate this value with the actual stream ID instead of choosing an arbitrary recent VOD by channel/title. `created_at` is when the video was created; `published_at` is when it was published. T5 defines stream `started_at` as when the broadcast began. These are different documented concepts: no fetched source guarantees that video creation time equals broadcast start time.

The APIs do not establish that local media timestamp zero equals Twitch VOD zero. An implementation must carry source provenance and an explicitly validated local-to-VOD mapping, account for trimmed/missing segments, and reject unmappable offsets. Matching `stream_id` establishes identity, not timestamp calibration. Verify a real timestamp link manually before claiming alignment.

T4 returns metadata and URLs, not raw gameplay frames or a general-purpose VOD download endpoint. Continue to use Clips Kitty's authorized source acquisition workflow.

### Authentication, nominations, and rate limits

T7 supports public clients through the device code grant flow without a distributed client secret. Twitch suggests public clients on open platforms such as Windows. The device authorization request uses registered `client_id` and requested `scopes`, returns a user verification URI/code and an `interval`, and token exchange uses the device grant type. Public clients are limited to that grant flow. Public-client refresh tokens are single use, must be replaced after exchange, and expire after 30 days of inactivity. This is documentation research, not a registered-client authorization test.

T8 requires any application maintaining a Twitch OAuth session to validate at startup and hourly. A revoked/invalid token must end affected sessions. `GET https://id.twitch.tv/oauth2/validate` returns identity, granted scopes, client ID, and expiry for validation; invalid tokens return 401.

T9 documents `channel.chat.message` version 1 with `broadcaster_user_id` and authenticated `user_id` conditions. It requires `user:read:chat`; an app-token flow additionally requires `user:bot` and either broadcaster `channel:bot` authorization or moderator status. The sample includes WebSocket transport. A local authorized user-token listener can receive nominations without inventing a plugin publisher stage. Retain only the minimum information needed for deduplication/cooldowns, and use nominations as supporting evidence.

T6 documents a token bucket, default point cost 1, separate app/user buckets, and user limits per client ID and user per minute. Read `Ratelimit-Limit`, `Ratelimit-Remaining`, and `Ratelimit-Reset`; on 429 honor the reset time. The displayed limit of 800 is an example, not a reason to hard-code that number. No endpoint-specific clip creation quota was established in the fetched sections.

## Competitor observations and blocked access

The following ordinary HTTPS requests failed with `Tunnel connection failed: 403 Forbidden` from this environment on the check date. No authentication or network restriction was bypassed.

| Target | URL attempted | What can be concluded |
| --- | --- | --- |
| Eklipse GTA landing page | https://eklipse.gg/use-case/gta/ | Page contents, GTA event claims, framing/caption controls, and ranking behavior could not be observed |
| Eklipse public site/blog | https://eklipse.gg/ and https://eklipse.gg/blog/ | No additional product evidence acquired |
| Athenascope | https://www.athenascope.com/ | Product behavior unavailable |
| Opus ClipAnything | https://www.opus.pro/clipanything | Product behavior unavailable |
| Powder | https://powder.gg/ | Product behavior unavailable |
| Combo | https://www.joincombo.com/ | Product behavior unavailable |
| Framedrop | https://www.framedrop.ai/ | Product behavior unavailable |
| Outplayed | https://go.overwolf.com/outplayed/ | Product behavior unavailable |
| Medal GTA V category | https://medal.tv/games/gta-v | Example footage and metrics unavailable |

The project brief identifies Eklipse as a reference; that is not verified evidence of a particular feature or algorithm. No inspectable Eklipse GTA plugin was obtained. This does not establish that none exists. No competitor model architecture, internal scoring, source code, or proprietary endpoint is asserted.

The observation worksheet remains unfilled until public content or an authorized workflow is accessible: source URL; retrieval time; input; visible output; event; timing/duration; setup/payoff; framing; captions; reaction/audio; useful behavior; failure; confidence; access limitation. Do not label this worksheet as completed competitor testing.

## Public GTA references and engagement evidence

No individually identified GTA video with independently verified engagement data was obtained. There are **zero verified viral reference cases** and no completed viral comparison. No counts, dates, creators, editing patterns, or clip durations have been inferred.

| Platform | Public discovery URL attempted | Result |
| --- | --- | --- |
| YouTube | https://www.youtube.com/results?search_query=GTA+V+funny+shorts | Network CONNECT 403 |
| TikTok | https://www.tiktok.com/tag/gtav | Network CONNECT 403 |
| Instagram | https://www.instagram.com/explore/tags/gtav/ | Network CONNECT 403 |
| Twitch | https://www.twitch.tv/directory/category/grand-theft-auto-v/clips | HTTP 200; category title/description present, client app shell contains no individual clip IDs or engagement counts |
| Web discovery | Google and Bing searches for GTA V roleplay funny Shorts | Network CONNECT 403 |

Twitch's documentation contains illustrative clip/view-count examples, including examples for other games. They are documentation fixtures, not observed public GTA engagement evidence, and must not enter a viral benchmark. Public clip discovery through Helix requires an authorized registered application token; no such token was supplied to this research task.

To complete the comparison, an operator should record individually accessible reference URLs and retrieval timestamps, then collect only publicly visible metrics. Leave unavailable likes/comments/shares as unknown. Compare categories and editing characteristics without downloading or redistributing video unless separately authorized. Engagement counts describe that publication and audience; they do not prove that a style caused the engagement.

## Hackathon rules verification

Both https://twitchcon-codex.devpost.com/ and https://twitchcon-codex.devpost.com/rules failed with network CONNECT 403. Current official eligibility, development window, deadline/time zone, intellectual property terms, submission fields, and demo constraints remain **unverified in this environment**. Do not claim compliance or an official deadline from this research.

The user brief states a November 2, 2026 deadline, a public YouTube demo under three minutes, real Twitch functionality, meaningful Codex use/session ID, source/setup availability, and disclosure of the pre-existing Clips Kitty application/SDK. Treat these as the supplied preparation requirements until the official rules are checked. The brief's GTA VI release timing and launch-platform statements were not independently checked here; no detector accuracy on GTA VI gameplay is asserted.

Before submission, open the official rules in a supported environment and record their last-updated date, official submission-period boundaries and time zone, eligibility, team limits, required fields, video length/publication rules, AI and prior-work disclosure rules, third-party asset requirements, and publication requirements. Record the actual Codex session ID through `/status` or the current client UI; do not invent a session ID from process names or environment variables.

## Independent requirements passed to implementation

These requirements follow verified API contracts and the user's desired behavior. They are not a reconstruction of competitor internals:

1. Clip only authorized channels/VODs; select minimal scopes and validate token identity/grants.
2. Keep native clip creation in reusable host integration. Pass actual VOD identity, validated end offset, bounded duration, and factual title.
3. Treat 202 as pending, retrieve the returned public URL, and preserve timestamp-link fallback when authorization, processing, or source availability prevents a native clip.
4. Distinguish input end offsets from returned start offsets and preserve unknown/null timeline state.
5. Associate an archive with its stream ID; require explicit calibration before mapping local detector timestamps into Twitch links.
6. Make viewer nominations affect review/ranking through explainable supporting evidence with cooldown and deduplication.
7. Preserve setup, event, and reaction when available; do not equate loudness or nominations with correctness. These editorial goals originate in the project brief, not verified viral examples.
8. Evaluate real authorized footage before claiming event accuracy, watchability, comparison to public references, or improvement. Synthetic tests validate behavior only.

Research and implementation contexts were separated at the task level, sharing only public API contracts and independent requirements. No proprietary internals were accessed. This process is **not represented as a legally strict independent clean room**.
