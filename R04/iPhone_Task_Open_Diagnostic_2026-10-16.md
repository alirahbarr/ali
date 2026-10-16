# iPhone task-opening diagnostic — 16 October 2026

Status: updated with the owner's completed comparison tests. The failure is isolated to the native app path in the tested cases; its underlying cause is not confirmed. No account, app, credential, or device access was performed. No support message was sent.

## What is established

Owner-reported observations:

- **All existing Codex tasks fail to open in the native ChatGPT iPhone app**, reporting: **“Codex could not open this task. Try again in a moment.”** This is not limited to the restaurant task.
- **The same task opens in Safari on the same iPhone using the same desktop account/workspace.** This browser comparison is complete; it does not need repeating.
- The device is described as an iPhone 18 Pro; the actual device model, iOS version and app build have not been independently checked.
- Closing the app and restarting the phone did not resolve the problem. Those steps need not be repeated.
- The task works in a desktop browser, and the project files can now be delivered through GitHub.

The Safari/app comparison isolates the observed failure to the native app's opening path or session in the tested cases. It does not distinguish an app-session/workspace problem from an app defect. The successful same-phone browser test provides a working phone access route. It does not establish an outage, an unsupported device, or the underlying cause. Working GitHub delivery is independent of ChatGPT's task-opening path.

## Official evidence retrieved

Public sources were retrieved on this review date using normal HTTPS/TLS verification:

| Source | Retrieval result | What it establishes |
|---|---|---|
| [OpenAI Codex README](https://github.com/openai/codex/blob/main/README.md), retrieved through [official raw file](https://raw.githubusercontent.com/openai/codex/main/README.md) | HTTP 200 | OpenAI identifies its cloud-based agent as Codex Web and directs users to `https://chatgpt.com/codex`. It links to the official Codex documentation and the Help Centre article about Codex in ChatGPT. |
| [OpenAI Codex authentication document](https://github.com/openai/codex/blob/main/docs/authentication.md), retrieved through [official raw file](https://raw.githubusercontent.com/openai/codex/main/docs/authentication.md) | HTTP 200 | This file is about CLI authentication and points to the official authentication documentation. It does not diagnose the mobile task-opening error. |

Both links use the repository's mutable `main` branch. Neither retrieved document states the cause of this exact error, confirms an iPhone task-opening feature matrix, or establishes an outage.

Direct official Help Centre, status and developer-document requests were previously reported as blocked by the environment's network proxy with HTTP 403. Their current page contents were not verified. Useful official destinations, **not represented as checked current guidance here**, are [OpenAI Help Centre](https://help.openai.com/), [OpenAI status](https://status.openai.com/) and the README-linked [Codex in ChatGPT article](https://help.openai.com/en/articles/11369540-codex-in-chatgpt).

## Next steps using the completed tests

1. **Use Safari for Codex on the phone.** The same task already opens there. Desktop and GitHub delivery also remain available. Do not delete or recreate the project to troubleshoot this app-opening issue.
2. **Check for an official App Store update.** Apply a ChatGPT update if one is offered, then retry the app once. The installed app build and iOS version remain unknown. An update is a troubleshooting step, not a demonstrated fix.
3. **Refresh the app's account/workspace context if needed.** Use the same account and active workspace as the working Safari session; if they already match, move to the next step. Do not change workspace permissions or subscription settings merely to diagnose this error.
4. **Sign out of the native app and sign back in if the failure continues.** Use the existing sign-in method and return to the same workspace. This refreshes the app session; it does not require a password reset. Do this only when the owner can complete their usual sign-in. Retry one existing task once.
5. **If all tasks still fail in the app, send the evidence to official support.** Include the confirmed Safari/app comparison and version information below. No repeat restart, force-close, other-task or Safari test is needed.

## Support report essentials

Use OpenAI's official Help Centre when accessible. Its current contact-interface labels have not been verified here. Supply:

- Exact quoted error and a screenshot showing it.
- Exact task URL/ID, identifying this as a Codex cloud-environment-onboarding task; provide the link privately to support.
- First failure time and a recent reproduction time with timezone, preferably `America/Toronto`.
- Actual device model, iOS version, ChatGPT app version/build, and whether an update is offered/applied.
- The confirmed results: all existing Codex tasks fail in the native iPhone app; the same task opens in Safari on that same iPhone with the same desktop account/workspace; desktop also works.
- Whether the app's account/workspace context was refreshed, and the result after an app update and sign-out/sign-in, if attempted.
- The fact that closing the app and restarting the phone were already attempted.

Do not attach the restaurant's design files, credentials, authentication cookies or access tokens to diagnose this opening error. Redact unrelated personal content from screenshots.

## Support copy-text

> All my existing Codex tasks fail to open in the native ChatGPT app on my iPhone 18 Pro. The exact error is: “Codex could not open this task. Try again in a moment.” The same task opens successfully in Safari on this same iPhone using the same desktop account/workspace, and it also works on desktop. Closing the app and restarting the phone did not help. Please investigate the native app's task-opening path/session. Task URL: [insert privately]. ChatGPT app version/build: [insert]. iOS version: [insert]. Latest failure time and timezone: [insert]. App update/sign-out/sign-in results, if tried: [insert].

The app and iOS versions remain unknown; obtain them for the support report if the problem persists. No additional diagnostic question is pending. There is insufficient evidence to claim an outage, an unsupported phone model, unavailable mobile support, a damaged task, or an account entitlement problem. Safari is the confirmed phone workaround.
