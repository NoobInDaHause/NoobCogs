# Suggestions Help

Suggestion system.<br/><br/>Have users submit suggestions to help improve some things.

# suggest (Hybrid Command)
 - Usage: `[p]suggest <suggestion> `
 - Slash Usage: `/suggest <suggestion> `
 - Cooldown: `1 per 10.0 seconds`
 - Checks: `guild_only`

Suggest stuff.

# approve
 - Usage: `[p]approve <suggestion_id> [reason] `
 - Restricted to: `ADMIN`
 - Checks: `guild_only`

Approve a suggestion.

# reject
 - Usage: `[p]reject <suggestion_id> [reason] `
 - Restricted to: `ADMIN`
 - Checks: `guild_only`

Reject a suggestion.

# suggestview
 - Usage: `[p]suggestview <suggestion_id> `
 - Aliases: `sv`

Check who downvoted or upvoted from a suggestion.

# suggestionset
 - Usage: `[p]suggestionset `
 - Restricted to: `ADMIN`
 - Aliases: `suggestset`
 - Checks: `guild_only`

Configure the suggestion cog.

## suggestionset buttoncolor
 - Usage: `[p]suggestionset buttoncolor <types> [colour=None] `
 - Aliases: `buttoncolour`

Change the upvote or downvotes button colour.<br/><br/>Leave colour blank to reset the colour of the type you put.<br/><br/>Available colours:<br/>- red<br/>- green<br/>- blurple<br/>- grey

## suggestionset editreason
 - Usage: `[p]suggestionset editreason <suggestion_id> <reason> `

Edit a suggestions reason.

## suggestionset resetcog
 - Usage: `[p]suggestionset resetcog `
 - Restricted to: `BOT_OWNER`

Reset the whole cogs configuration.

## suggestionset emoji
 - Usage: `[p]suggestionset emoji <vote> [emoji=None] `

Change the UpVote or DownVote emoji.

## suggestionset allowselfvote
 - Usage: `[p]suggestionset allowselfvote `
 - Aliases: `asv`

Toggle whether to allow suggestion authors to upvote or downvote their own suggestion or not.

## suggestionset reset
 - Usage: `[p]suggestionset reset `

Reset the guilds settings to default.

## suggestionset showsettings
 - Usage: `[p]suggestionset showsettings `
 - Aliases: `ss`

Show the current suggestion cogs guild settings.

## suggestionset channel
 - Usage: `[p]suggestionset channel <type> [channel=None] `
 - Aliases: `chan`

Set the suggestion channel.<br/><br/>Leave channel blank to remove the current set channel on what type you used.<br/>Rejection channel and Approved channel are optional.

## suggestionset autodelete
 - Usage: `[p]suggestionset autodelete `
 - Aliases: `autodel`

Toggle whether to automatically delete suggestion commands or not.