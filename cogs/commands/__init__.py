from .hello import helloCog


def setup(bot):
    bot.add_cog(helloCog(bot))