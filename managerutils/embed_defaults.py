# <----- GIVEAWAYS EMBED DATA ----->
# AVAILABLE VARIABLES:
# {prize} - the giveaway prize
# {sponsor} - the sponsor
# {message} - the sponsor message
# {host} - the host username
# {host.name} - the host name
# {host.display_name} - the host guild nickname
# {host.mention} - mentions the host
# {host.id} - the host ID
# {guild} - the guild name
# {guild.icon_url} - the guild image

gembed_description = "**Prize:** {prize}\n**Sponsor:** {sponsor}\n**Message:** {message}"
gembed_footer_icon = "{host.avatar_url}"
gembed_footer_text = "Hosted by: {host}"
gembed_image = ""
gembed_thumbnail = ""
gembed_title = "Server Giveaway Time!"

# <----- EVENTS EMBED DATA ----->
# {host} - the host
# {host.name} - The host name
# {host.display_name} - the host guild nickname
# {host.mention} - mentions the host
# {host.id} - the host ID
# {guild} - the guild name
# {guild.icon_url} - The guild image
# {sponsor} - the sponsor
# {eventname} - the name of the event
# {prize} - the event prize
# {message} - the sponsor message

eembed_description = ""
eembed_footer_icon = "{host.avatar_url}"
eembed_footer_text = "Hosted by: {host}"
eembed_image = ""
eembed_thumbnail = "{guild.icon_url}"
eembed_title = "Server Event Time!"
eembed_sponsor_field_name = "Event Sponsor:"
eembed_sponsor_field_value = "{sponsor}"
eembed_name_field_name = "Event Name:"
eembed_name_field_value = "{eventname}"
eembed_prize_field_name = "Event Prize:"
eembed_prize_field_value = "{prize}"
eembed_message_field_name = "Message:"
eembed_message_field_value = "{message}"

# <----- HEISTS EMBED DATA ----->
# {host} - the host
# {host.name} - The host name
# {host.display_name} - the host guild nickname
# {host.mention} - mentions the host
# {host.id} - the host ID
# {guild} - the guild name
# {guild.icon_url} - The guild image
# {sponsor} - the sponsor
# {amount} - the heist amount
# {requirements} - the requirements
# {message} - the sponsor message

hembed_description = ""
hembed_footer_icon = "{host.avatar_url}"
hembed_footer_text = "Hosted by: {host}"
hembed_image = ""
hembed_thumbnail = "{guild.icon_url}"
hembed_title = "Server Heist Time!"
hembed_sponsor_field_name = "Heist Sponsor:"
hembed_sponsor_field_value = "{sponsor}"
hembed_amount_field_name = "Amount:"
hembed_amount_field_value = "{amount}"
hembed_requirements_field_name = "Requirements:"
hembed_requirements_field_value = "{requirements}"
hembed_checklist_field_name = "Checklist:"
hembed_checklist_field_value = "` - ` Have a life saver on your inventory.\n` - ` Withdraw at least **1** coin.\n` - ` Press the big green `JOIN HEIST` button."
hembed_message_field_name = "Message:"
hembed_message_field_value = "{message}"