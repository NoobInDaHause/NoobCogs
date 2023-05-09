import random

class SosGifs:
    #  <----- FORFEIT GIFS ----->
    def forfeitgif():
        f1 = "https://cdn.discordapp.com/attachments/1087623489130872832/1087624656212733963/pink-panther-pink.gif"
        f2 = "https://cdn.discordapp.com/attachments/1087623489130872832/1087623551978319903/eh-meh.gif"
        f3 = "https://cdn.discordapp.com/attachments/1087623489130872832/1087623774431621201/nathan-ing-twitch-streamer.gif"

        fimg = [f1, f2, f3]
        return random.choice(fimg)

    # <----- WIN GIFS ----->
    def wingif():
        w1 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084840480489099304/tom-jerry-playing-clg846ldrq2w0l6b.gif"
        w2 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084841885803237427/high-five-amy-santiago.gif"
        w3 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084842629520425160/385b1w_1.gif"
        w4 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084844274367082566/high-five_1.gif"
        w5 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084844732766748772/wedding-crasher-hro_1.gif"

        wimg = [w1, w2, w3, w4, w5]
        return random.choice(wimg)

    # <----- BETRAY GIFS ----->
    def betraygif():
        b1 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084805789677531226/tf2-spy.gif"
        b2 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084819894505324674/Sheperd_Betrayal.gif"
        b3 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084835711355719790/icegif-634.gif"
        b4 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084837146822717480/laughing-kangaroo.gif"
        b5 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084838240923693116/AdolescentUnlawfulDungenesscrab-max-1mb_1.gif"
        b6 = "https://cdn.discordapp.com/attachments/1005509686302359562/1087623151933997056/emotional-damage_1.gif"

        bimg = [b1, b2, b3, b4, b5, b6]
        return random.choice(bimg)

    # <----- LOSE GIFS ----->
    def losergif():
        l1 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084826566841872425/clothesline_collision.gif"
        l2 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084827437411602503/17wM.gif"
        l3 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084829936407281664/1.gif"
        l4 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084834072548888687/collision-knights_1.gif"
        l5 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084845839157039104/gta-grand-theft-auto_1.gif"

        limg = [l1, l2, l3, l4, l5]
        return random.choice(limg)
    
class SosHelp:
    em1desc = """
        The game involves a segment called `Split or Steal` in which two participants or players make the decision to either `split` or `steal` and to determine how the prize is divided or stolen.
        
        The game also determines the ones who are good or evil.
        
        The game requires 2 participants or players to play.
        
        A very fun game to play.
        
        :warning: This game can shatter friendships! Play at your own risk!
        
        Happy playing! :)
        ** **
        """

    em2desc = """
        The rules are pretty simple, you have two choices `split` or `steal`.
        ` - ` If both participants or players chose `split` then they both split the prize and everyone is a winner.
        ` - ` If one player chooses `split` and the other player chooses `steal` the bad person who chose steal gets all the prize!
        ` - ` If both players or participants chose `steal` nobody wins the prize cause they are both bad. :joy:
        :warning: Be warned trust no one in this game. ;)
        ** **
        """

    em3desc = """
        The game works by running `[p]splitorsteal <player_1> <player_2> <prize>`.
        You will need 2 players and a prize to start the game.
        You can not play the game with discord bots. Noob.

        Once the command is ran the bot now sets up the game.
        The bot will now tell both the participants to think very carefully and to discuss whether they want to `split` or `steal`.

        Once the minute is up the bot now sends the players a DM's and letting them choose `split` or `steal`.
        Players must have their DM's open! Otherwise the game gets cancelled.

        If one of the players did not respond to the bots DM's they will automatically forfeit the game.
        If one of the players fail to answer `split` or `steal` they will automatically forfeit the game. It's 2 simple choices how did you still mess up??
        The bot also accepts emojis but it only accepts 🤝 for `split` or ⚔️ for `steal` please don't say anything else besides that.

        Then when everything is set we will now see who the bad or the good person is.
        It may be both good or both bad or one good and one bad.
        ** **
        """