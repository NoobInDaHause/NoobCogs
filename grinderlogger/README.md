# GrinderLogger Help

GrinderLogger system.<br/><br/>Manage grinders from your server.

# grinderlogger
 - Usage: `[p]grinderlogger `
 - Aliases: `grlog`
 - Checks: `guild_only`

GrinderLogger base commands.

## grinderlogger demote
 - Usage: `[p]grinderlogger demote <member> <tier> [reason] `
 - Checks: `GrinderLogger`

Demote a grinder.

## grinderlogger stats
 - Usage: `[p]grinderlogger stats [member=None] `

Check your or someone else's grinder stats.

## grinderlogger promote
 - Usage: `[p]grinderlogger promote <member> <tier> [reason] `
 - Checks: `GrinderLogger`

Promote a grinder.

## grinderlogger dono
 - Usage: `[p]grinderlogger dono <_type> <member> <amount> [time=None] `
 - Checks: `GrinderLogger`

Add or remove grinder donation amount and time.

## grinderlogger leaderboard
 - Usage: `[p]grinderlogger leaderboard `
 - Aliases: `lb`

Show the grinderlogger leaderboard.

# grinderloggerset
 - Usage: `[p]grinderloggerset `
 - Restricted to: `ADMIN`
 - Aliases: `grlogset`
 - Checks: `guild_only`

GrinderLogger settings commands.

## grinderloggerset removemember
 - Usage: `[p]grinderloggerset removemember <member> [reason] `

Remove a grinder.

## grinderloggerset resetguild
 - Usage: `[p]grinderloggerset resetguild `

Reset the guild GrinderLogger system.

## grinderloggerset resetcog
 - Usage: `[p]grinderloggerset resetcog `
 - Restricted to: `BOT_OWNER`

Reset cog config.

## grinderloggerset manager
 - Usage: `[p]grinderloggerset manager <add_or_remove_or_list> <roles> `

Add, remove, or check the list of grinder managers.

## grinderloggerset channel
 - Usage: `[p]grinderloggerset channel <_type> [channel=None] `
 - Aliases: `chan`

Add or remove grinder related channels idk.

## grinderloggerset dmstatus
 - Usage: `[p]grinderloggerset dmstatus `

Toggle whether to DM the member for their grinder promotion/demotion.

## grinderloggerset tier
 - Usage: `[p]grinderloggerset tier <_type> <tier> <role> [amount=None] `
 - Aliases: `t`

Add or remove tier amount roles.

## grinderloggerset addmember
 - Usage: `[p]grinderloggerset addmember <member> <tier> [reason] `

Add a member as a grinder.

## grinderloggerset donationloggersupport
 - Usage: `[p]grinderloggerset donationloggersupport [bank_name=None] `
 - Aliases: `dlsupport`

Add support for DonationLogger.

## grinderloggerset showsettings
 - Usage: `[p]grinderloggerset showsettings `
 - Aliases: `ss`

Show GrinderLogger settings.