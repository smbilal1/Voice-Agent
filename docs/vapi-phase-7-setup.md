# Phase 7: Vapi Assistant and Phone Number

This phase provisions the callable U.S. phone number. Do not use real patient information during tests.

## 1. Create the Assistant

1. Sign in to [Vapi Dashboard](https://dashboard.vapi.ai) and open **Assistants**.
2. Select **Create Assistant**, then choose **Blank Template**.
3. Set the name to `CareCloud Patient Registration`.
4. Keep Vapi's **Balanced** preset initially. It bundles an LLM, transcriber, and voice and is the fastest reliable starting point.
5. Set the first message to:

   ```text
   Thank you for calling CareCloud. I'm Ava, the virtual intake coordinator. I can help register you as a new patient. Is now a good time to begin?
   ```

6. Turn on interruptions for the first message, so callers can answer naturally.
7. Set the maximum call duration to 8 minutes.
8. Turn background sound off for a clean clinical intake experience.
9. Save or publish the Assistant.
10. Copy its ID into your local `.env` as `VAPI_ASSISTANT_ID`.

The complete patient-registration system prompt and backend tools are intentionally added in Phase 8.

## 2. Provision a U.S. number

1. Open **Phone Numbers** → **Create Phone Number**.
2. Choose **Free Vapi Number**.
3. Choose a preferred U.S. area code, if Vapi offers one.
4. Name it `CareCloud Patient Registration Line`.
5. In **Inbound Settings**, select `CareCloud Patient Registration` as the Assistant.
6. Save the assignment.
7. Copy the full E.164 number (for example, `+14155552671`) into `.env` as `VAPI_PHONE_NUMBER`.

## 3. Safe smoke test

Use Vapi's **Talk to Assistant** test first, then place a call from your own phone. Confirm that it:

- answers with the first message;
- allows interruption;
- understands a normal spoken response; and
- ends the call normally.

At this stage it will not create patient records yet; the API tools are added in Phase 8.

## 4. Keep these values private

- `VAPI_API_KEY`: secret; only in `.env` / Railway variables.
- `VAPI_WEBHOOK_SECRET`: secret; only in `.env` / Railway variables and Vapi Custom Credential configuration.
- `VAPI_ASSISTANT_ID`: non-secret but useful for operations.
- `VAPI_PHONE_NUMBER`: include this in the final submission README, not as a secret.

## 5. Ready for Phase 8

Once the number answers correctly, Phase 8 will add the conversational prompt, `create_patient` tool, server authentication, duplicate lookup, confirmation workflow, and call completion behavior.
