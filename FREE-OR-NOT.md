# FREE-OR-NOT

This is a quick reminder for how `aicp-free-now.md` works.

The app fetches this file from:

```text
https://wuu73.org/aicp/aicp-free-now.md
```

It is used for two things:

1. temporarily turning Pro on for everyone
2. showing optional popup notices

## Cache behavior

The result is cached locally for about 15 minutes.

That means if you change the server file from `free=1` to `free=0`, or change a message, users may keep the old value for up to roughly 15 minutes.

## Free flag

### `free=1`

Use this when you want to temporarily let everyone use Pro features.

Effect:

- non-paid users are treated like Pro users
- paid users still remain paid users as normal
- Pro-gated features unlock for everyone during this period

### `free=0`

Use this when you want to end the temporary free-Pro period.

Effect:

- only verified paid users keep Pro
- free users go back to normal free mode

## Notice keys

There are now two separate notice channels.

### 1. General notice for everyone

Use one of these keys:

- `message=`
- `msg=`
- `notice=`

This popup can show to everyone.

That includes:

- paid users
- free users
- users who currently have temporary Pro because of `free=1`

Example:

```text
free=1
message=General announcement here.
```

### 2. Free-user-only notice

Use one of these keys:

- `free_user_message=`
- `free_user_msg=`
- `free_user_notice=`
- `free_message=`
- `free_msg=`
- `free_notice=`

This popup is only meant for users who are not currently Pro-enabled.

So it is the right one for:

- discounts for free users
- a reminder after the free-Pro period ends
- upgrade prompts that should not bother paid users

Example:

```text
free=0
free_user_message=Pro is no longer temporarily free.\nFor a limited time, you can get 50% off a lifetime license.
```

## Recommended patterns

### Offer Pro free for a while

```text
free=1
```

Optional general note to everybody:

```text
free=1
message=Everything is temporarily unlocked right now.
```

### End the free period and show a promo only to free users

```text
free=0
free_user_message=Pro is no longer temporarily free.\nFor a limited time, you can get 50% off a lifetime license.
```

### Show a general maintenance or release note to everybody

```text
free=0
message=Maintenance notice: new pricing page and updated docs are now live.
```

## Popup behavior

The popup is shown once per distinct final text.

That means if you leave the message text exactly the same, users should not keep getting spammed with it on every startup.

If you change the text, it is treated as a new notice.

## Notes

- Comments and blank lines are ignored.
- `\n` inside a message becomes a real line break in the popup.
- If the fetch fails, the app falls back to `free=0` and no message.
- Verified paid users still short-circuit Pro access even if the remote flag system is unavailable.

## Good default future use

If you want the cleanest setup later, this is probably the one you will use:

```text
free=0
free_user_message=Pro is no longer temporarily free.\nFor a limited time, you can get 50% off a lifetime license.
```
