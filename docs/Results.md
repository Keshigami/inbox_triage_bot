# Results

No metrics file; the measurable part is the six-sample table. Offline (no key in the build environment) the match
count is 1/6 because the door answers the first option (`Sales`) every time; it is the floor. With a key, 6/6 is
expected on these clear cases. The tests prove: deterministic output, empty input rejected, `URGENT` -> `High`,
`slack:#support` -> `Slack #support`, unknown route -> derived from category, every routing line labelled
`[SIMULATED]`, and the UI reaching a result from one click.
