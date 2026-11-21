# Hackathon verification record

Current detector source is frozen 0.5.2 at `6ab55bd`. This documentation update does
not alter that implementation, its version, the installed pin or its immutable
package. The original 0.4.1 checkout and outputs remain preserved.

| Check | Result | Evidence and limits |
|---|---|---|
| Original 0.4.1 baseline |Recorded pass|251 tests, SDK validation with 3 known warnings, generic sample with 0 GTA moments and authored horizontal/vertical exports. This is baseline evidence, not 0.5.2 quality.|
| Independent 0.5.2 implementation |Pass at frozen source|358 tests, Ruff and SDK validation; [CI 40529063606](https://github.com/ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin/actions/runs/40529063606) succeeded. Fictional tests cover joint discovery, boundaries, mapped nominations, budgets, timeout/cache behavior and invalid siblings.|
| Actual app full-source candidate |Completed|28 clips using the same source/real cached ASR and matched host. All 28 audio/full-decode checks passed. See [EKLIPSE_COMPARISON.md](EKLIPSE_COMPARISON.md); limited model coverage is explicit.|
| Timing review |User accepted shorter style|Jail, street-question and impound examples reviewed. Keep existing shorter intervals; longer output remains configurable. This is not a blind rubric for all clips.|
| Gaming manual facecam |Pass in actual host|All 28 existing cuts re-rendered with Draw it, source facecam above gameplay. 1080x1920 with audio; full decode, unchanged intervals/durations/titles, original backups, actual picker/source frame, visible gallery and MCP export verified. No detector change.|
| Live Twitch viewer connection |Host evidence, separate source|Real zackrawrr metadata, EventSub chat, restart persistence and archive link passed in clips-studio PR 194. Zackrawrr is not the GTA quality source. No live GTA nomination/clock-alignment success is claimed.|
| Untouched holdout / blind quality |Not run; deferred|Explicit fast-submission priority. No precision, recall, parity or GTA VI gameplay claim.|
| Live WoopSocial delivery |Not run; host follow-up|Existing connection reads and local export do not prove a platform post. No social post was sent.|
| Public demo / publication |Not performed|The 2:17 recording was clarified as a test. Real Fanum workflow drafts remain private; source use for a final public entry requires Colin's confirmation.|

Private artifact records remain outside this repository:

- Actual candidate run: `D:/ck-hackathon/fanum-candidate-comparison/cases.json`.
- Accepted review: `review/Fanum-GTA-Timing-Review.mp4` under that comparison folder.
- Corrected actual Gaming outputs: `D:/ck-hackathon/gaming-facecam-repair/verification.json`.
- Host test/runtime log: `clips-studio/docs/hackathon/TEST_LOG.md`.

Discord and date scheduling are excluded by Colin's latest scope. No Store
upload, stable catalog promotion or PR merge is included in this verification.
