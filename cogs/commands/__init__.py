from .test import testCog


def setup(bot):
    bot.add_cog(testCog(bot))
