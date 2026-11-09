# Ops Inbox Triage Bot

Paste an email and get category, urgency, a one-line summary and a suggested route, validated by pydantic, with the routing shown as simulated log lines. Portfolio, Automation Engineer, by Maximus Friedrich Baluyot.

**Watch first:** [the 90-second film](https://github.com/Keshigami/inbox_triage_bot/blob/main/demo/film.mp4).

## Pages
- [Getting started](Getting-Started.md): run it in three commands, what you see, the API.
- [How it was built](How-It-Was-Built.md): from the brief to a running service, step by step.
- [Results](Results.md): the numbers and what they mean.
- [Limits and next steps](Limits-and-Next-Steps.md): what it cannot do yet.
- [The film](The-Film.md): what the four chapters show.

## The brief
A shared ops inbox mixes sales leads, outages, invoice disputes, press requests and spam, and the lead that matters
waits behind the noise. This bot reads one email and returns a structured record (category, urgency, summary, route)
that a router can act on. Solved means every email is pre-sorted in seconds and the record is always on-schema, so
downstream automation never sees a malformed answer.

## The one-line answer
0 · messages sent · every route line is [SIMULATED]

## One honest limit
Offline answers Sales every time: one of six.
