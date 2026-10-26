# Real GTA footage review

Historical 0.3.0 review. For the current 0.4.1 actual-app/MCP comparison, failure
regressions and review video method, see [MCP review](MCP_REVIEW.md).

Recorded 2026-10-25. This is development evaluation, not a blind test or a
claim of superiority over another service. Media and full transcripts stay
outside this repository; this report contains references and derived measurements.

## Method

Reuse the basketball review method: acquire a concrete source, cache actual
local Whisper output, run the real SDK/app, inspect source and exported frames,
record false/missed selections, and add regression checks for observed failures.
The basketball implementation was not copied into this MIT plugin.

Actual sources include public YouTube videos from DarkViperAU, Vista Gamer
and Crulfy, and public Twitch clips from buddha and summit1g. Discovery metrics
were captured from the primary services and may change. The final stream cases
use two full YouTube recordings with a visible facecam, with fixed 180-second
excerpts at source 300-480 seconds:

- [DarkViperAU stream, part 217](https://www.youtube.com/watch?v=op3LIcOB4GU).
- [DarkViperAU stream, part 218](https://www.youtube.com/watch?v=p4QDaQdZmXA).

Both excerpts use the same local Whisper transcript, local `gemma4:e4b`, quality
threshold and Gaming split layout for the baseline and specialized path. Settings
and history are isolated from the normal app. The normal app's shared AI setting
was preserved; it currently selects OpenRouter. The SDK only receives the local
model when the host is configured for one; it never receives a cloud key.

## Concrete fixes from shorter sources

| Public source | 0.2.0 | Updated detector | Scope |
|---|---|---|---|
| [DarkViperAU vehicle incident](https://www.youtube.com/watch?v=Uqub0AtkX5s) | No candidate | Vehicle incident, source 0-14 s | Spoken spin-out cue; no physical object detector claimed |
| [Vista Gamer](https://www.youtube.com/watch?v=-rOOTD6-Tfc) | No candidate | Collision 0-15.1 s and combat commentary 29.9-48.6 s | Limited Spanish phrases, preserving negation and plans |
| [buddha celebration](https://clips.twitch.tv/HotConsiderateClintmullinsWOOP--hrFMzuxC8xBa8AH) | No candidate | One reaction window 0-36.17 s | Repeated celebration joined instead of two short repeats; no claim the earlier heist is visible |
| [Crulfy quiet incident](https://www.youtube.com/watch?v=DZuaN6kcKXw) | No candidate | Still missed | Background vehicle falls with almost no usable speech |

Both arms use the same source, actual transcript, optional local-model access
and a maximum of three candidates. These are inspected development examples,
not representative event-accuracy statistics. Added original fictional tests
exercise equivalent phrases and negative cases without redistributing speech.

## Facecam stream findings

The transcript-only event rules initially returned no candidates on the sampled
full streams even while the shared Gaming finder produced clips. A spoken
survival-wave progress update exposed another missing GTA event type. The updated
plugin adds an explicit mission-progress category and a generic title that does
not invent a wave count. Source intervals, hashes and final runs are recorded in
[real-footage.json](../evaluation/results/real-footage.json).

Earlier development runs combined generic and GTA finding. That interpretation
was rejected by the owner and is not the final integration. In those runs, one
normal-model re-run produced an extra conversation clip; the GTA stage found none.
That difference is model-run variability, not a GTA detector improvement.
The final Gaming selection delegates finding to the specialized GTA pipeline.

The final specialized run selected one mission-progress window at excerpt
134.54-172.32 seconds in part 217, or source 434.54-472.32 seconds. Part 218
returned no candidates rather than falling back to generic conversation clips.
The generic baseline selected one clip in each excerpt. These counts do not
establish which detector has better coverage or engagement. The mission window
also includes unrelated subscriber thanks and conversation: word-level boundary
refinement and metadata relevance remain improvements to evaluate. The host's
generated title emphasized the subscriber thanks rather than mission progress.

Five development MP4 exports were decoded and inspected: each had 1080x1920
video, audio, burned captions, visible facecam/game regions and isolated history.
The final specialized MP4 was decoded and checked separately with the same layout.
Its measured duration includes the host's end card. The host's image-input probe
failed for this installed Gemma4 model, so its vision-confirmation stage skipped.
No visual detection accuracy or general watchability improvement is inferred.
Mixed chatting/GTA is allowed; a platform game tag is not a factual event label.

## Eklipse comparison status

The requested baseline is Eklipse's actual hosted GTA output on identical source
footage. It is **not completed**. No Eklipse GTA model weights or supported public
inference API were established. An account or existing project/results link is
needed before a same-input comparison can be recorded. The owner confirmed they
do not have Eklipse access. No generated Eklipse result, score or superiority claim
has been invented, and the authored energy-only reference is not Eklipse.

Eklipse's [engine description](https://blog.eklipse.gg/streaming-tips/how-gameplay-intelligence-works-2.html)
describes genre tuning and scene context. Its [YouTube import guide](https://eklipse.gg/help/how-to-make-a-highlight-reel-from-youtube-videos-with-eklipse/)
uses the hosted app and account workflow. These public descriptions supply
comparison dimensions, not model code. Save its actual project/version, source
intervals and exports before comparing event support, setup/payoff, duplicates,
facecam/game retention, captions and unnecessary quiet material.

The owner also supplied Eklipse's [GTA use-case page](https://eklipse.gg/use-case/gta/)
and [GTA 6 clip tool](https://eklipse.gg/tool/gta-6-clips-tool/), reviewed on
2026-10-25. The latter describes a free browser tool that reframes, captions and
exports an already selected clip through its shared GTA tool. It explicitly
leaves automatic GTA VI detection unconfirmed. Its output can inform editing
review, but cannot establish VOD event-finding or ranking accuracy. We did not
run that browser editor or infer any proprietary model implementation from it.

The final integration remains GTA-specific finding and ranking with the host's
existing FFmpeg and renderer, as confirmed by the owner. FFmpeg installation in
CI provisions an ephemeral test runner; the plugin does not install a second
FFmpeg or renderer into Clips Kitty.

## Remaining limits

Quiet action without an explicit supported cue can be missed. Spanish support
is a small set of conservative cues, not general translation. Local model
corroboration does not make an event a verified visual fact. Live viewer chat,
OAuth, native Twitch clip creation and Discord posting were not performed here.
No GTA VI gameplay, public demo upload, Store package or Devpost submission was
produced. None of these checks establishes a causal engagement improvement.
