from redbot.core.utils.chat_formatting import box

class SdonateDesc:
    """
    Long ass descriptions.
    """
    gcmd = "Syntax: [p]giveawaydonate <type> | <duration> | <winners> | [requirements] | <prize> | [message]\nAlias: [p]gdonate, [p]gdono"
    gdonodesc = f"""
        {box(gcmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Duration**
        ` - ` The duration is how long would the giveaway last.
        **Winners**
        ` - ` The amount of winners for the giveaway.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `None` if you do not want any requirements.
        **Prize**
        ` - ` The prize of the giveaway.
        **Message**
        ` - ` Send an optional message to the giveaway.
        ` - ` Type `None` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `None` if you do not want to put anything.
        
        Examples:
            `[p]giveawaydonate "Dank Memer" "1 day and 12 hours" 1w none "69 coins" hallo guys welcome to my minecraft channel.`
            `[p]gdonate dank 1d12h 1w none 420coins free 420 coins!!`
        """
        
    ecmd = "Syntax: [p]eventdonate <type> | <event> | [requirements] | <prize> | [message]\nAlias: [p]]edonate, [p]edono"
    edonodesc = f"""
        {box(ecmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Event**
        ` - ` The type of event that you want to sponsor. (this can be any event or games that users can play)
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `None` if you do not want any requirements.
        **Prize**
        ` - ` The prize of the event.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `None` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `None` if you do not want to put anything.
        
        Examples:
            `[p]eventdonate "Owo bot" "Split Or Steal" none "1m owo coins" can i have chezburger plz`
            `[p]edonate owobot splitorsteal none 1mowocoins mmmmmm chezburger`
        """
        
    hcmd = "Syntax: [p]heistdonate <type> | [requirements] | <amount> | [message]\nAlias: [p]hdonate, [p]hdono"
    hdonodesc = f"""
        {box(hcmd, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        **Amount**
        ` - ` The amount that you want to donate.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `None` if you do not want to send a message.
        
        Notes:
            You must split arguments with `|`.
            Arguments surrounded by [] are optional put `None` if you do not want to put anything.
        
        Examples:
            `[p]heistdonate "Bro Bot" none "69420 coins" heist this shit up`
            `[p]hdonate brobot none 69420coins bored so heres a heist for yall`
        """